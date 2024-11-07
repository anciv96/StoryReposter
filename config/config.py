import json
from os import getenv

import aiofiles
import dotenv

dotenv.load_dotenv()


class ConfigManager:
    config_file = 'config/config.json'

    @staticmethod
    async def load_config():
        """Загружает настройки из JSON-файла."""
        async with aiofiles.open(ConfigManager.config_file, mode='r') as file:
            content = await file.read()
            return json.loads(content)

    @staticmethod
    async def save_config(data: dict):
        """Сохраняет переданный словарь настроек в JSON-файл."""
        async with aiofiles.open(ConfigManager.config_file, mode='w') as file:
            await file.write(json.dumps(data, indent=4))

    @staticmethod
    async def get_setting(key: str):
        """Получает значение конкретной настройки по ключу."""
        config = await ConfigManager.load_config()
        return config.get(key)

    @staticmethod
    async def set_setting(key: str, value):
        """Устанавливает значение для конкретной настройки и сохраняет файл."""
        config = await ConfigManager.load_config()
        config[key] = value
        await ConfigManager.save_config(config)


SESSIONS_UPLOAD_DIR = 'content/accounts'
PROXIES_UPLOAD_DIR = 'content/proxies'
USERNAMES_LIST_DIR = 'content/usernames_list'
LAST_STORY_CONTENT_DIR = 'content/stories'
OWNER = int(getenv("OWNER"))
TOKEN = getenv("BOT_TOKEN")
