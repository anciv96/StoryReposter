import os

from aiogram import Router, F
from aiogram.filters import Command, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.backend.services.account_service import AccountService
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.account_keyboard import minus_kb
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.states.import_account_state import ImportAccount
from app import logger_setup
from app.utils.folder_utils import clear_directory, download_file, extract_rar_file, extract_zip_file
from config.config import SESSIONS_UPLOAD_DIR, PROXIES_UPLOAD_DIR


import_account = Router(name=__name__)
logger = logger_setup.get_logger(__name__)


@import_account.message(and_f(
    or_f(
        Command('import_account'),
        F.text == '📥 Импорт аккаунтов'),
    IsAdminFilter(True)
))
async def command_import_account_handler(message: Message, state: FSMContext) -> None:
    await AccountService.clear_cache()
    await message.answer("Пожалуйста, загрузите архив аккаунтов в формате .rar или .zip")
    await state.set_state(ImportAccount.archive_file)
    await state.set_state(ImportAccount.archive_file)


@import_account.message(ImportAccount.archive_file)
async def get_file_handler(message: Message, state: FSMContext) -> None:
    file_name = message.document.file_name
    if message.document is None:
        await state.clear()
        await message.answer('Ошибка: Поддерживаются только ZIP и RAR файлы.')
        return

    file_path = os.path.join(SESSIONS_UPLOAD_DIR, file_name)

    if file_name.endswith('.rar') or file_name.endswith('.zip'):
        await clear_directory(SESSIONS_UPLOAD_DIR)
        await download_file(message, SESSIONS_UPLOAD_DIR)
        await _extract_archive_file(message, file_path)

        await message.answer('Пожалуйста, загрузите .txt-файл с прокси в формата soaks5 ввиде api:port:login:password. '
                             'Если прокси отсутствуют, то поставьте -. Каждая прокси должна вводится с отдельной строки'
                             'без разделителей в конце строки.', reply_markup=minus_kb)
        await state.set_state(ImportAccount.proxy_file)
    else:
        await message.answer('Отмена импорта...')
        await message.reply("Неизвестный формат архива. Поддерживаются только ZIP и RAR.", reply_markup=menu_kb)
        await state.clear()


async def _extract_archive_file(message: Message, file_path: str):
    if message.document.file_name.endswith('.zip'):
        await extract_zip_file(file_path)

    elif message.document.file_name.endswith('.rar'):
        await extract_rar_file(file_path)


@import_account.message(ImportAccount.proxy_file)
async def get_proxy(message: Message, state: FSMContext) -> None:
    await state.clear()

    if message.text != '-':
        if message.document is None:
            await message.answer('Ошибка: Принимается только .txt файл.', reply_markup=menu_kb)
            return

        await clear_directory(PROXIES_UPLOAD_DIR)

        await download_file(message, PROXIES_UPLOAD_DIR)
        await message.answer('Прокси сохранены.', reply_markup=menu_kb)
    else:
        await message.answer('Архив аккаунтов сохранен.', reply_markup=menu_kb)
