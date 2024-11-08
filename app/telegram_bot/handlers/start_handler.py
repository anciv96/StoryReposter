from aiogram import Router
from aiogram.filters import CommandStart, and_f, or_f, Command
from aiogram.types import Message

from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb

start_router = Router(name=__name__)


@start_router.message(and_f(or_f(CommandStart(), Command('menu')), IsAdminFilter(True)))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        "Добро пожаловать в бот Mass Tagger! 🤖\n\n"
        "🔥 Основные возможности:\n"
        "• Поддержка нескольких аккаунтов для эффективного тегинга\n"
        "• Умная интеграция прокси для повышенной надежности\n"
        "• Возможность массового импорта пользователей\n"
        "• Автоматический механизм повторных попыток с умной обработкой ошибок\n"
        "• Управление ограничениями для предотвращения блокировки аккаунтов\n\n"
        "📋 Доступные команды:\n"
        "➕ Добавить аккаунт - Добавить новый аккаунт Telegram вручную\n"
        "📥 Импорт аккаунтов - Импортировать несколько аккаунтов из ZIP/RAR архива\n"
        "Просмотр аккаунтов - Посмотреть добавленные аккаунты \n"
        "📝 Загрузить список - Загрузить список пользователей для теггинга\n"
        "▶️ Начать теггинг - Начать операцию тегинга в указанном чате\n"
        "⏹️ Остановить теггинг - Остановить текущую операцию тегинга\n"
        "Настройки – Посмотреть текущие настройки и внести изменения",
        reply_markup=menu_kb
    )
