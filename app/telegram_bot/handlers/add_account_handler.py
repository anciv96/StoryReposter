import asyncio
from random import uniform
from typing import Optional, Any

from aiogram import Router, F
from aiogram.filters import Command, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from telethon.errors import SessionPasswordNeededError

from app import logger_setup
from app.backend.services.account_service import AccountService
from app.exceptions.account_exceptions import ProxyIsNotValidError, PhoneNumberIsNotValidError
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.account_keyboard import minus_kb
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.states.add_account_state import AddAccountState
from app.utils.proxy_utils import add_proxy, convert_proxy, check_proxy

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
    await message.answer("Напишите номер телефона в формате 79………. (формат можно через +)", reply_markup=menu_kb)
    await state.set_state(AddAccountState.phone)


@add_account_router.message(AddAccountState.phone)
async def process_phone(message: Message, state: FSMContext):
    """
    Processes the user's phone number and requests the API ID.
    """
    await state.update_data(phone=message.text)
    await message.answer("Введите api_id", reply_markup=menu_kb)
    await state.set_state(AddAccountState.api_id)


@add_account_router.message(AddAccountState.api_id)
async def process_api_id(message: Message, state: FSMContext):
    """
    Processes the user's API ID and requests the API hash.
    """
    await state.update_data(app_id=message.text)
    await message.answer("Введите api_hash", reply_markup=menu_kb)
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
    try:
        proxy_input = message.text
        proxy = await _get_proxy(proxy_input)
        await state.update_data(proxy=proxy)
    except ProxyIsNotValidError as error:
        logger.error(error)
        await state.clear()
        return

    user_data = await state.get_data()
    client_data = await _create_client(user_data, proxy)
    if client_data is None:
        await state.clear()
        return

    client, phone_code_hash = client_data
    await AccountService.clear_cache()

    await state.update_data(client=client, phone_code_hash=phone_code_hash)
    await message.answer("На ваш Telegram аккаунт пришел код авторизации. Введите код авторизации.",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddAccountState.code)


async def _get_proxy(proxy_input) -> Optional[dict]:
    if proxy_input == '-':
        return None
    else:
        proxy = await convert_proxy(proxy_input)
        await check_proxy(proxy)
        await add_proxy(proxy_input)
        return proxy


async def _create_client(user_data: dict, proxy: dict) -> Optional[tuple[Any, Any]]:
    try:
        client, phone_code_hash = await AccountService.create_client(
            phone=user_data.get('phone'),
            app_id=int(user_data.get('app_id')),
            app_hash=user_data.get('app_hash'),
            proxy=proxy
        )
        return client, phone_code_hash
    except ValueError:
        logger.error('Ошибка: app_id должен быть целым числом')
        if client:
            await client.disconnect()
    except PhoneNumberIsNotValidError:
        logger.error('Номер не найден')
        if client:
            await client.disconnect()
    except Exception as error:
        logger.error(f'Ошибка: что-то пошло не так: {error}')
        if client:
            await client.disconnect()

    return None


@add_account_router.message(AddAccountState.code)
async def process_code(message: Message, state: FSMContext):
    """
    Processes the authorization code and completes the account addition if successful.
    Requests 2FA password if necessary.
    """
    user_data = await state.get_data()
    code = message.text.replace(' ', '')
    client = user_data['client']
    try:
        await AccountService.sign_in(client=client,
                                     phone=user_data['phone'],
                                     code=code,
                                     phone_code_hash=user_data['phone_code_hash'],
                                     )

        if await client.is_user_authorized():
            await message.answer("Аккаунт успешно добавлен!", reply_markup=menu_kb)
            logger.info(f'Account {user_data["phone"]} saved successfully')
        else:
            await message.answer("Ошибка: не удалось авторизовать аккаунт.", reply_markup=menu_kb)
            logger.info('Account not saved')
            return

        await asyncio.sleep(uniform(5, 7))
        await client.disconnect()
        await state.clear()

    except SessionPasswordNeededError:
        await message.answer("Введите пароль 2FA.", reply_markup=menu_kb)
        await state.set_state(AddAccountState.two_fa_password)
    except Exception as e:
        logger.error(f"Ошибка при авторизации: {e}")
        await client.disconnect()
        await state.clear()
        await message.answer("Ошибка авторизации. Проверьте введённые данные.")


@add_account_router.message(AddAccountState.two_fa_password)
async def process_two_fa_password(message: Message, state: FSMContext):
    """
      Processes the 2FA password and completes the account setup.
    """
    user_data = await state.get_data()
    password = message.text
    client = user_data['client']
    try:
        await AccountService.sign_in_with_password(client, password=password)
        await message.answer("Аккаунт успешно добавлен!", reply_markup=menu_kb)
    except Exception as e:
        logger.error(f"Ошибка при входе: {e}")
        await message.answer("Ошибка при входе. Проверьте пароль и попробуйте снова.")
    finally:
        await asyncio.sleep(uniform(4, 7))
        await client.disconnect()
        await state.clear()
