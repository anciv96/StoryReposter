from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.backend.schemas.account import Account
from app.backend.services.account_service import AccountService
from config.config import ConfigManager


class MyCallback(CallbackData, prefix="accounts"):
    action: str
    page: int
    account_id: str


async def get_accounts_keyboard(current_page: int = 0):
    accounts = await AccountService.get_all_accounts()
    keyboard = InlineKeyboardBuilder()
    start = current_page * await ConfigManager.get_setting('items_per_page')
    end = start + await ConfigManager.get_setting('items_per_page')
    current_accounts = accounts[start:end]

    for account in current_accounts:
        keyboard.add(
            InlineKeyboardButton(
                text=str(account.phone),
                callback_data=MyCallback(action="delete", page=current_page, account_id=account.phone).pack()
            )
        )

    keyboard.adjust(2)

    navigation_buttons = await _add_navigation_buttons(accounts, current_page, end)
    if navigation_buttons:
        keyboard.row(*navigation_buttons)

    return keyboard.as_markup()


async def _add_navigation_buttons(accounts: list[Account], page: int, end: int) -> list[InlineKeyboardButton]:
    navigation_buttons = []

    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⏮️",
                callback_data=MyCallback(action="first", page=page, account_id='0').pack()

            )
        )

    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=MyCallback(action="prev", page=page, account_id='0').pack()

            )
        )

    if (len(accounts) - 1) // await ConfigManager.get_setting('items_per_page') != 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=f"{page}/{(len(accounts) - 1) // await ConfigManager.get_setting('items_per_page')}",
                callback_data=MyCallback(action="", page=page, account_id=0).pack()

            )
        )

    if end < len(accounts):
        navigation_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=MyCallback(action="next", page=page, account_id=0).pack()

            )
        )
    if end < len(accounts):
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⏭️",
                callback_data=MyCallback(action="last", page=len(accounts) - 1, account_id=0).pack()

            )
        )

    return navigation_buttons
