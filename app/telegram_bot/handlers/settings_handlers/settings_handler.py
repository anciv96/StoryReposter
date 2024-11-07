from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, and_f, or_f

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.settings_keyboard import settings_kb

settings_router = Router(name=__name__)
logger = logger_setup.get_logger(__name__)


@settings_router.message(and_f(
    or_f(
        Command('settings'),
        F.text == 'Настройки – Посмотреть текущие настройки и внести изменения'),
    IsAdminFilter(True)
))
async def settings_command_handler(message: Message):
    await message.answer('Настройки:', reply_markup=settings_kb)
