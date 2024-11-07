import os

from aiogram import Router, F
from aiogram.filters import Command, or_f, and_f
from aiogram.types import Message, CallbackQuery

from app import logger_setup
from app.backend.schemas.account import Account
from app.backend.services.account_service import AccountService
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.inline.show_accounts_kb import get_accounts_keyboard, MyCallback
from config.config import ConfigManager

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
        accounts = await AccountService.get_all_accounts()
        if len(accounts) > 0:
            await message.answer("Добавленные аккаунты. Чтобы удалить, нажмите на кнопку с номером",
                                 reply_markup=await get_accounts_keyboard())
        else:
            await message.answer("Нет активных аккаунтов")
    except Exception as error:
        logger.error(error)


@show_accounts.callback_query(MyCallback.filter())
async def handle_pagination(callback_query: CallbackQuery, callback_data: MyCallback):
    action = callback_data.action
    page = callback_data.page
    account_phone = callback_data.account_id
    accounts = await AccountService.get_all_accounts()

    account_path = await _get_account_path(accounts, account_phone)

    if action == "delete":
        os.remove(account_path)
        await AccountService.clear_cache()
        await callback_query.message.edit_reply_markup()
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


async def _get_account_path(accounts: list[Account], account_phone: str):

    for account in accounts:
        if account.phone == account_phone:
            return account.session_file
