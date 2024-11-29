import asyncio

from app.telegram_bot.handlers.settings_handlers.admins_settings_handler import admins_list_router
from app.telegram_bot.handlers.settings_handlers.max_usernames_per_sessions_handler import max_usernames_router
from app.telegram_bot.handlers.stop_tagging import stop_tagging_router
from config.dispatcher import dp, bot
from app import logger_setup
from app.telegram_bot.handlers.add_account_handler import add_account_router
from app.telegram_bot.handlers.add_usernames_handler import add_usernames_router
from app.telegram_bot.handlers.import_account_handler import import_account
from app.telegram_bot.handlers.settings_handlers.period_settings_handler import period_settings_router
from app.telegram_bot.handlers.settings_handlers.posting_delay_settings_handler import posting_delay_settings_router
from app.telegram_bot.handlers.settings_handlers.settings_handler import settings_router
from app.telegram_bot.handlers.settings_handlers.show_settings_handler import show_settings_settings_router
from app.telegram_bot.handlers.settings_handlers.tegs_settings_handler import tags_settings_router
from app.telegram_bot.handlers.show_accounts_handler import show_accounts
from app.telegram_bot.handlers.start_handler import start_router
from app.telegram_bot.handlers.start_tagging import start_tagging_router

logger = logger_setup.get_logger(__name__)


async def main():
    dp.include_router(start_router)
    dp.include_router(import_account)
    dp.include_router(add_account_router)
    dp.include_router(add_usernames_router)
    dp.include_router(start_tagging_router)
    dp.include_router(stop_tagging_router)
    dp.include_router(show_accounts)

    dp.include_router(period_settings_router)
    dp.include_router(settings_router)
    dp.include_router(posting_delay_settings_router)
    dp.include_router(tags_settings_router)
    dp.include_router(max_usernames_router)
    dp.include_router(show_settings_settings_router)
    dp.include_router(admins_list_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
