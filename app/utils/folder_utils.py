import os
import shutil
import zipfile
from typing import Optional

import rarfile
from aiogram.types import Message

from app import logger_setup
from config.config import SESSIONS_UPLOAD_DIR, LAST_STORY_CONTENT_DIR
from config.dispatcher import bot

logger = logger_setup.get_logger(__name__)


async def clear_directory(directory_path):
    """Cleans all data in the directory."""
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f'Не удалось удалить {file_path}. Причина: {e}')


async def download_file(message: Message, upload_dir: str) -> str:
    file_path = os.path.join(upload_dir, message.document.file_name)
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, file_path)

    return file_path


async def get_txt_file_path(directory: str) -> Optional[str]:
    txt_file = next((f for f in os.listdir(directory) if f.endswith('.txt')), None)
    if not txt_file:
        raise FileNotFoundError('Txt file not found')

    file_path = os.path.join(directory, txt_file)
    return file_path


async def get_usernames(directory: str) -> list[str]:
    """
    Searches for a .txt file in the specified directory, reads usernames from it,
    and returns them as a list of strings.

    Args:
        directory (str): Path to the directory containing the .txt file with usernames.

    Returns:
        List[str]: A list of usernames (e.g., ['@username1', '@username2']) or an empty list if no valid file is found.
    """
    try:
        file_path = await get_txt_file_path(directory)
    except FileNotFoundError:
        raise FileNotFoundError

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            usernames = [line.strip() for line in file if line.startswith('@') and len(line.strip()) > 1]
        return usernames
    except UnicodeDecodeError:
        logger.error("Ошибка декодирования: файл должен быть в кодировке UTF-8.")
    except Exception as e:
        logger.error(f"Ошибка обработки файла {file_path}: {e}")

    return []


async def delete_directory(directory_path: str) -> None:
    """Deletes the directory"""
    shutil.rmtree(directory_path)


async def extract_zip_file(zip_path):
    with zipfile.ZipFile(zip_path, 'r', metadata_encoding="utf-8") as archive:
        archive.extractall(SESSIONS_UPLOAD_DIR)


async def extract_rar_file(rar_path):
    with rarfile.RarFile(rar_path, 'r') as archive:
        archive.extractall(SESSIONS_UPLOAD_DIR)


async def get_first_media_file(directory: str = LAST_STORY_CONTENT_DIR) -> Optional[str]:
    try:
        files = sorted(os.listdir(directory))
        media_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.mov'))]

        if media_files:
            return os.path.join(directory, media_files[0])
        else:
            logger.error("No story files found in the directory.")
            return None
    except FileNotFoundError:
        return None
