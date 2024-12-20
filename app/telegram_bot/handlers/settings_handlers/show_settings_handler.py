from aiogram import F, Router
from aiogram.filters import and_f
from aiogram.types import Message

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from config.config import ConfigManager

logger = logger_setup.get_logger(__name__)
show_settings_settings_router = Router(name=__name__)


@show_settings_settings_router.message(and_f(
    F.text == 'Посмотреть настройки',
    IsAdminFilter(True)
))
async def tags_handler(message: Message) -> None:
    story_period = await ConfigManager.get_setting('story_period')
    posting_delay = await ConfigManager.get_setting('posting_delay')
    tags_per_story = await ConfigManager.get_setting('tags_per_story')
    max_usernames_per_session = await ConfigManager.get_setting('max_usernames_per_session')

    message_text = (f'Задержка между постингом – <b>{posting_delay}</b> секунд\n'
                    f'Время нахождения сторис в профиле -  <b>{story_period}</b> часов/часа\n'
                    f'Количество отметок с одного аккаунта – <b>{tags_per_story}</b> отметок с одного аккаунта\n'
                    f'Максимальное количество отметок с одного аккаунта – <b>{max_usernames_per_session}</b> '
                    f'отметок с одного аккаунта\n'
                    )

    await message.answer(message_text, reply_markup=menu_kb)
