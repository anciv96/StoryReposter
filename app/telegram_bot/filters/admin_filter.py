from aiogram.filters import Filter
from aiogram.types import Message

from config.config import ConfigManager, OWNER


class IsAdminFilter(Filter):
    def __init__(self, is_admin: bool) -> None:
        self.is_admin = is_admin

    async def __call__(self, message: Message) -> bool:
        admins: list = await ConfigManager.get_setting('admins_ids')
        admins.extend(OWNER)
        if self.is_admin:
            return message.from_user.id in admins
        else:
            return message.from_user.id not in admins
