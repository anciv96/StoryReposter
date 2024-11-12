from aiogram import Router, F
from aiogram.filters import Command, or_f, and_f
from aiogram.types import Message, CallbackQuery

from app import logger_setup
from app.backend.services.account_service import AccountService
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.keyboards.inline.show_accounts_kb import get_accounts_keyboard, MyCallback
from app.utils.folder_utils import delete_directory, delete_file_in_nested_folders
from config.config import ConfigManager, SESSIONS_UPLOAD_DIR

show_accounts = Router(name=__name__)
logger = logger_setup.get_logger(__name__)


@show_accounts.message(and_f(
    or_f(
        Command('show_accounts'),
        F.text == 'Просмотр аккаунтов'
    ),
    IsAdminFilter(True)
))
async def command_show_accounts_handler(message: Message) -> None:
    try:
        await AccountService.clear_cache()
        accounts = await AccountService.get_all_accounts()
        if len(accounts) > 0:
            await message.answer("Добавленные аккаунты. Чтобы удалить, нажмите на кнопку с номером",
                                 reply_markup=await get_accounts_keyboard())
        else:
            await message.answer("Нет активных аккаунтов", reply_markup=menu_kb)
    except Exception as error:
        logger.error(error)


@show_accounts.callback_query(MyCallback.filter())
async def handle_pagination(callback_query: CallbackQuery, callback_data: MyCallback):
    action = callback_data.action
    page = callback_data.page
    account_phone = callback_data.account_id
    accounts = await AccountService.get_all_accounts()

    if action == "delete":
        await delete_directory(f'{SESSIONS_UPLOAD_DIR}/{account_phone}')
        await delete_file_in_nested_folders(SESSIONS_UPLOAD_DIR, f'{account_phone}.json')
        await delete_file_in_nested_folders(SESSIONS_UPLOAD_DIR, f'{account_phone}.session')
        await AccountService.clear_cache()
        await callback_query.message.answer(f'Аккаунт {account_phone} успешно удален!')
    elif action == "first":
        await callback_query.message.edit_reply_markup(reply_markup=await get_accounts_keyboard(0))
    elif action == "prev":
        await callback_query.message.edit_reply_markup(reply_markup=await get_accounts_keyboard(page - 1))
    elif action == "next":
        await callback_query.message.edit_reply_markup(reply_markup=await get_accounts_keyboard(page + 1))
    elif action == "last":
        await callback_query.message.edit_reply_markup(
            reply_markup=await get_accounts_keyboard((len(accounts) - 1) // await ConfigManager.get_setting('items_per_page'))
        )
