from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, or_f, and_f
from aiogram.fsm.context import FSMContext

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.states.add_usernames_list_state import AddUsernamesState
from app.utils.folder_utils import download_file, clear_directory
from config.config import USERNAMES_LIST_DIR

add_usernames_router = Router(name=__name__)
logger = logger_setup.get_logger(__name__)


@add_usernames_router.message(and_f(
    or_f(
        Command('add_usernames'),
        F.text == '📝 Загрузить список'),
    IsAdminFilter(True)
))
async def prompt_for_usernames_file(message: Message, state: FSMContext):
    """
    Handles the /add_usernames command by prompting the user to upload a .txt file containing
    usernames in the format @username on each new line.
    """
    await message.reply(
        "Загрузите .txt-файл со списком пользователей для теггинга. "
        "В формате @username на новой строке."
    )
    await state.set_state(AddUsernamesState.file)


@add_usernames_router.message(AddUsernamesState.file)
async def handle_usernames_file(message: Message, state: FSMContext):
    """
    Processes the uploaded .txt file, verifies its format, and parses usernames if valid.
    """
    await state.clear()
    if message.document is None:
        await message.answer('Ошибка: Принимается только .txt файл.', reply_markup=menu_kb)
        return

    if not message.document.file_name.endswith('.txt'):
        await message.reply("Ошибка загрузки. Пожалуйста, загрузите файл с расширением .txt.", reply_markup=menu_kb)
        return

    try:
        await clear_directory(USERNAMES_LIST_DIR)
        file_path = await download_file(message, USERNAMES_LIST_DIR)
        usernames_count = await process_usernames_file(file_path)

        if usernames_count > 0:
            await message.reply(f"Список успешно загружен. Добавлено {usernames_count} пользователей для теггинга.",
                                reply_markup=menu_kb)
        else:
            await message.reply(
                "Проверьте список пользователей. Файл должен содержать валидные @username на новой строке.",
                reply_markup=menu_kb)
    except FileNotFoundError:
        logger.error("Ошибка: не удалось найти путь к файлу.")
        await message.reply("Ошибка обработки файла. Попробуйте еще раз.")
    except IOError as e:
        logger.error(f"Ошибка ввода-вывода: {e}")
        await message.reply("Ошибка при обработке файла. Попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        await message.reply("Произошла непредвиденная ошибка. Пожалуйста, попробуйте снова.")


async def process_usernames_file(file_path: str) -> int:
    """
    Reads a .txt file, filters for valid usernames (lines starting with @),
    and returns the count of valid usernames found.

    Args:
        file_path (str): Path to the uploaded .txt file.

    Returns:
        int: Number of valid usernames found in the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            usernames = [line.strip() for line in file if line.startswith('@') and len(line.strip()) > 1]
        return len(usernames)
    except FileNotFoundError:
        logger.error("Файл не найден.")
        return 0
    except UnicodeDecodeError:
        logger.error("Ошибка декодирования: файл должен быть в кодировке UTF-8.")
        return 0
    except Exception as e:
        logger.error(f"Ошибка обработки файла: {e}")
        return 0
