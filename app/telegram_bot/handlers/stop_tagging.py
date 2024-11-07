from aiogram import Router, F
from aiogram.filters import Command, or_f, and_f
from aiogram.types import Message

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from config.config import ConfigManager

stop_tagging_router = Router(name=__name__)
logger = logger_setup.get_logger(__name__)


@stop_tagging_router.message(and_f(
    or_f(
        Command('stop_tagging'),
        F.text == '⏹️ Остановить теггинг'),
    IsAdminFilter(True)
))
async def stop_tagging_handler(message: Message):
    await ConfigManager.set_setting('turned_on', False)
    await message.reply("Работа теггинга успешно остановлена")
