import os

from telethon import TelegramClient
from telethon.tl.functions.stories import GetPeerStoriesRequest
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

from app import logger_setup
from app.backend.schemas.account import Account
from app.backend.services.story_services.story_service import StoryService
from app.exceptions.account_exceptions import NotAuthenticatedError
from app.exceptions.story_exceptions import NoActiveStoryError
from config.config import SESSIONS_UPLOAD_DIR, LAST_STORY_CONTENT_DIR


logger = logger_setup.get_logger(__name__)


class DownloadStoryService(StoryService):
    async def download_last_story(self, target_account: str, account: Account) -> tuple[str, str]:
        """
        Downloads the latest story from the target account.

        :param target_account: The username or ID of the target account to download the story from.
        :param account: The account instance that will be used to download the story.
        :return: A tuple containing the path to the downloaded media and the type ('photo' or 'video').
        :raises NoActiveStoryError: If there are no active stories.
        """
        client = TelegramClient(account.session_file, account.app_id, account.app_hash)
        await client.connect()
        if await client.is_user_authorized():
            await client.disconnect()
            async with TelegramClient(account.session_file, account.app_id, account.app_hash) as client:
                target_entity = await client.get_entity(target_account)
                peer_stories = await client(GetPeerStoriesRequest(peer=target_entity))

                if not peer_stories.stories:
                    raise NoActiveStoryError("No active stories found for the target account.")

                last_story = peer_stories.stories.stories[-1]
                media = last_story.media

                if isinstance(media, MessageMediaPhoto):
                    media_path = self._generate_media_path(target_account, 'jpg')
                    media_type = 'photo'
                elif isinstance(media, MessageMediaDocument):
                    media_path = self._generate_media_path(target_account, 'mp4')
                    media_type = 'video'
                else:
                    raise TypeError("Unsupported media type in story.")

                await client.download_media(media, media_path)
                return media_path, media_type
        else:
            raise NotAuthenticatedError()

    def _generate_media_path(self, account_name: str, extension: str) -> str:
        """
        Generates a media file path for the downloaded story.

        :param account_name: The target account name for naming the media file.
        :param extension: File extension based on the media type.
        :return: Path string for saving the media file.
        """
        filename = f"{account_name}_latest_story.{extension}"
        return os.path.join(LAST_STORY_CONTENT_DIR, filename)
