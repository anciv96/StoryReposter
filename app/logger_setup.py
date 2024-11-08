import asyncio
import logging

from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from config.config import OWNER, ConfigManager
from config.dispatcher import bot


class TelegramHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    async def emit(self, record):
        log_entry = str(self.format(record))
        admins = await ConfigManager.get_setting('admins_ids')
        await bot.send_message(chat_id=OWNER, text=log_entry, parse_mode=None)
        for admin in admins:
            try:
                await bot.send_message(chat_id=admin, text=log_entry, parse_mode=None,
                                       reply_markup=menu_kb)
            except Exception:
                continue

    def handle(self, record):
        asyncio.create_task(self.emit(record))


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = '%(asctime)s - %(lineno)s - %(name)s - %(levelname)s - %(message)s'

    # Print в терминал
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(formatter))

    # Обработчик для файла
    file_handler = logging.FileHandler('error.log')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(formatter))

    # Telegram-обработчик
    telegram_handler = TelegramHandler()
    telegram_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter(formatter))

    # Добавляем обработчики в логгер
    logger.addHandler(file_handler)
    logger.addHandler(telegram_handler)
    logger.addHandler(console_handler)

    return logger
