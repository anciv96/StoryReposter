from typing import Optional, Any

from aiogram import Router, F
from aiogram.filters import Command, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from app import logger_setup
from app.backend.services.account_service import AccountService
from app.exceptions.account_exceptions import ProxyIsNotValidError, PhoneNumberIsNotValidError
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.account_keyboard import minus_kb
from app.telegram_bot.states.add_account_state import AddAccountState

add_account_router = Router(name=__name__)
logger = logger_setup.get_logger(__name__)


@add_account_router.message(and_f(
    or_f(Command('add_account'),
         F.text == '➕ Добавить аккаунт',
         ),
    IsAdminFilter(True)
))
async def command_add_account_handler(message: Message, state: FSMContext) -> None:
    """
    Initiates the process of adding a Telegram account.
    Asks the user to input their phone number.
    """
    await message.answer("Напишите номер телефона в формате 79………. (формат можно через +)")

    await state.set_state(AddAccountState.phone)


@add_account_router.message(AddAccountState.phone)
async def process_phone(message: Message, state: FSMContext):
    """
    Processes the user's phone number and requests the API ID.
    """
    await state.update_data(phone=message.text)
    await message.answer("Введите api_id")
    await state.set_state(AddAccountState.api_id)


@add_account_router.message(AddAccountState.api_id)
async def process_api_id(message: Message, state: FSMContext):
    """
    Processes the user's API ID and requests the API hash.
    """
    await state.update_data(app_id=message.text)
    await message.answer("Введите api_hash")
    await state.set_state(AddAccountState.api_hash)


@add_account_router.message(AddAccountState.api_hash)
async def process_api_hash(message: Message, state: FSMContext):
    """
    Processes the API hash and requests the proxy details.
    """
    await state.update_data(app_hash=message.text)
    await message.answer("Введите прокси формата soaks5 ввиде api:port:login:password. "
                         "Если прокси отсутствуют, то поставьте –.", reply_markup=minus_kb)
    await state.set_state(AddAccountState.proxy)


@add_account_router.message(AddAccountState.proxy)
async def process_proxy(message: Message, state: FSMContext):
    """
    Processes the proxy settings, creates a Telegram client, and requests the authorization code.
    """
    client = await _get_client(message, state)
    if client is None:
        return

    client, phone_code_hash = client

    await AccountService.clear_cache()

    await state.update_data(client=client, phone_code_hash=phone_code_hash)
    await message.answer("На ваш Telegram аккаунт пришел код авторизации. Введите код авторизации.",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddAccountState.code)


async def _get_client(message: Message, state: FSMContext) -> Optional[tuple[Any, Any]]:
    try:
        user_data = await state.get_data()
        proxy = message.text
        client, phone_code_hash = await AccountService.create_client(
            phone=user_data['phone'],
            app_id=int(user_data['app_id']),
            app_hash=user_data['app_hash'],
            proxy_input=None if proxy == '-' else proxy,
        )
        return client, phone_code_hash
    except ValueError:
        logger.error('Ошибка: app_id должен быть целым числом')
        await state.clear()
        return
    except ProxyIsNotValidError:
        await state.clear()
        return
    except PhoneNumberIsNotValidError:
        logger.error('Номер не найден')
        await state.clear()
        return
    except Exception as error:
        logger.error(f'Ошибка: что-то пошло не так: {error}')
        await state.clear()
        return


@add_account_router.message(AddAccountState.code)
async def process_code(message: Message, state: FSMContext):
    """
    Processes the authorization code and completes the account addition if successful.
    Requests 2FA password if necessary.
    """
    user_data = await state.get_data()
    code = message.text.replace(' ', '')

    try:
        await AccountService.sign_in(client=user_data['client'],
                                     phone=user_data['phone'],
                                     code=code,
                                     phone_code_hash=user_data['phone_code_hash'])
        await message.answer("Аккаунт успешно добавлен!")
        await state.clear()

    except SessionPasswordNeededError:
        await message.answer("Введите пароль 2FA.")
        await state.set_state(AddAccountState.two_fa_password)


@add_account_router.message(AddAccountState.two_fa_password)
async def process_two_fa_password(message: Message, state: FSMContext):
    """
      Processes the 2FA password and completes the account setup.
    """
    user_data = await state.get_data()
    password = message.text
    try:
        await AccountService.sign_in_with_password(client=user_data['client'], password=password)
        await message.answer("Аккаунт успешно добавлен!")
    except Exception as e:
        logger.error(f"Ошибка при входе: {e}")
    finally:
        await state.clear()
