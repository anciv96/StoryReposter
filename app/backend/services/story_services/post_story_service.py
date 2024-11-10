import asyncio
from itertools import islice

from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, SessionPasswordNeededError

from app import logger_setup
from app.backend.schemas.account import Account
from app.backend.services.story_services.story_service import StoryService
from app.exceptions.account_exceptions import NotAuthenticatedError
from config.config import ConfigManager

logger = logger_setup.get_logger(__name__)


class PostStoryService(StoryService):
    """
        Service for managing the publication of stories and mass marking of users.

        It implements functions for publishing stories on uploaded accounts and adding
        marks according to the specified parameters.
    """
    async def post_story_with_tags(self, client: Account, story, tags: list[str], proxy=None):
        """
        Publishes a story on an account and tags users in batches with a delay between each batch.

        :param client: The account to post the story on
        :param story: The story content
        :param tags: List of users to tag
        :param proxy: Proxy to prevent bans
        """
        batch_size = await ConfigManager.get_setting('tags_per_story')

        for batch in self._chunked_tags(tags, batch_size):
            turned_on = await ConfigManager.get_setting('turned_on')
            if not turned_on:
                return

            await self._post_story_with_batch(client, story, batch, proxy)

            posting_delay = await ConfigManager.get_setting('posting_delay')
            await asyncio.sleep(posting_delay)

    async def _post_story_with_batch(self, client: Account, story, batch: list[str], proxy=None):
        try:
            caption = await self._get_description(users_to_mention=batch)
            await self._post_story(client, story, caption, proxy)
        except FloodWaitError as e:
            logger.error(f"Flood wait error: {e}")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            await ConfigManager.set_setting('turned_on', False)
            logger.error(f"Неизвестная ошибка: {e}")

    def _chunked_tags(self, tags: list[str], batch_size: int) -> list[list[str]]:
        iterator = iter(tags)
        for first in iterator:
            yield [first, *islice(iterator, batch_size - 1)]

    async def _get_description(self, users_to_mention: list[str]) -> str:
        description = ' '.join(users_to_mention)
        return description

    async def _post_story(self, account: Account, story, caption, proxy=None) -> None:
        client = TelegramClient(account.session_file, account.app_id, account.app_hash,
                                device_model='Iphone 12 pro max', proxy=proxy)

        max_retries = 5
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(0.5)
                await client.connect()
                if not await client.is_user_authorized():
                    raise NotAuthenticatedError()

                media = await client.upload_file(story)
                try:
                    await client(functions.stories.SendStoryRequest(
                        peer=await client.get_me(),
                        media=types.InputMediaUploadedPhoto(
                            file=media
                        ),
                        privacy_rules=[types.InputPrivacyValueAllowContacts()],
                        caption=caption,
                        period=await ConfigManager.get_setting('story_period') * 3600
                    ))
                    logger.info(f'Отмечено {caption} аккаунтом {account.phone} (прокси: {proxy})')
                    break
                except Exception:
                    await client(functions.stories.SendStoryRequest(
                        peer=await client.get_me(),
                        media=types.InputMediaUploadedPhoto(
                            file=media
                        ),
                        privacy_rules=[types.InputPrivacyValueAllowContacts()],
                        caption=caption,
                    ))
                    logger.info(f'Отмечено {caption} аккаунтом {account.phone} (прокси: {proxy})')
                    break

            except FloodWaitError as e:
                logger.error(f"Flood wait error: {e}")
                await asyncio.sleep(e.seconds)

            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Ошибка подключения (попытка {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(5)

            except SessionPasswordNeededError:
                logger.error(f"{account.phone} требует двухфакторной аутентификации.")
                break

            except NotAuthenticatedError:
                logger.error(f'{account.phone} требует код подтверждения')
                break

            except Exception as e:
                logger.error(f"Неизвестная ошибка: {e}")
                break
            finally:
                await client.disconnect()

