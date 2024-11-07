from app.backend.services.story_services.story_service import StoryService

import asyncio
from itertools import islice

from telethon.errors import FloodWaitError

from app import logger_setup
from app.backend.schemas.account import Account
from config.config import ConfigManager


logger = logger_setup.get_logger(__name__)


class PostStoryService(StoryService):
    """
    Сервис для управления публикацией сторис и массовыми отметками пользователей.

    Реализует функции для публикации сторис на загруженных аккаунтах и добавления
    отметок в соответствии с заданными параметрами.
    """
    from itertools import islice

    async def post_story_with_tags(self, client: Account, story, tags: list[str], proxy=None):
        """
        Publishes a story on an account and tags users in batches with a delay between each batch.

        :param client: The account to post the story on
        :param story: The story content
        :param tags: List of users to tag
        :param proxy: Proxy to prevent bans
        :param batch_size: Number of users to tag per batch
        """
        batch_size = await ConfigManager.get_setting('tags_per_story')

        for batch in self._chunked_tags(tags, batch_size):
            turned_on = await ConfigManager.get_setting('turned_on')
            if not turned_on:
                return

            await self._post_story_with_batch(client, story, batch, proxy)

            # Wait before posting the next batch
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
            logger.error(f"Unexpected error: {e}")

    def _chunked_tags(self, tags: list[str], batch_size: int) -> list[list[str]]:
        iterator = iter(tags)
        for first in iterator:
            yield [first, *islice(iterator, batch_size - 1)]

    async def _get_description(self, users_to_mention: list[str]) -> str:
        description = ' '.join(users_to_mention)
        return description

    async def _post_story(self, account: Account, story, caption, proxy=None):
        """session_path = f'{SESSIONS_UPLOAD_DIR}/{account.session_file}/{account.session_file}.session'

        async with TelegramClient(
            session_path,
            account.app_id,
            account.app_hash,
            device_model='Iphone 12 pro max',
            proxy=proxy
        ) as client:

            await client(functions.stories.SendStoryRequest(
                peer=await client.get_me(),
                media=types.InputMediaUploadedPhoto(
                    file=await client.upload_file(story)
                ),
                privacy_rules=[types.InputPrivacyValueAllowContacts()],
                caption=caption,
                period=STORY_PERIOD

            ))"""
        print(f'{account.phone} -> tagged {caption} -> with proxy {proxy}')
