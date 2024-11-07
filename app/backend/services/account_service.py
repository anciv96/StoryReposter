import json
import os
from typing import Optional

from asyncache import cached
from cachetools import TTLCache
from telethon import TelegramClient

from app import logger_setup
from app.backend.schemas.account import Account
from app.exceptions.account_exceptions import PhoneNumberIsNotValidError
from app.utils.proxy_utils import add_proxy
from config.config import SESSIONS_UPLOAD_DIR


cache = TTLCache(maxsize=100, ttl=60)
logger = logger_setup.get_logger(__name__)


class AccountService:

    @staticmethod
    async def create_client(phone: str, app_id: int, app_hash: str, proxy_input: str = None) -> tuple:
        """
        Initializes and connects a Telegram client.
        Returns the client and the phone code hash required for authorization.
        """
        try:
            if proxy_input is not None:
                await add_proxy(proxy_input)

            session_path = await AccountService._get_session_path(phone)
            client = TelegramClient(session_path, app_id, app_hash)

            await client.connect()
            model = await client.send_code_request(phone)
            return client, model.phone_code_hash
        except TypeError:
            raise PhoneNumberIsNotValidError

    @staticmethod
    async def _get_session_path(phone: str):
        try:
            account_path = os.path.join(SESSIONS_UPLOAD_DIR, phone)
            os.makedirs(account_path, exist_ok=True)
            session_path = os.path.join(account_path, str(phone))
            return session_path
        except Exception as error:
            logger.error(error)

    @staticmethod
    async def sign_in(client: TelegramClient, phone: str, code: str, phone_code_hash: str) -> None:
        """
        Signs in the user using the provided code.
        """
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        await AccountService.save_login_data(phone, client.api_id, client.api_hash, client.session.filename)

    @staticmethod
    async def sign_in_with_password(client: TelegramClient, password: str) -> None:
        """
        Signs in the user using their 2FA password.
        """
        await client.sign_in(password=password)

        phone = str(client.session.filename).split('/')[-1].replace('.session', '')

        await AccountService.save_login_data(phone, client.api_id, client.api_hash, client.session.filename)

    @staticmethod
    async def save_login_data(phone: str, api_id: int, api_hash: str, session_file: str,
                              username: Optional[str] = None) -> None:
        """
        Saves login details in a JSON file in the account directory, using the Account model.
        """
        account_path = os.path.dirname(session_file).replace('.session', '')
        json_path = os.path.join(account_path, f"{phone}.json")

        # Create an Account instance and save it to JSON
        account = Account(
            session_file=phone,
            phone=phone,
            app_id=api_id,
            app_hash=api_hash,
            username=username
        )

        with open(json_path, 'w') as json_file:
            json.dump(account.dict(), json_file, indent=4)

    @staticmethod
    @cached(cache)
    async def get_all_accounts() -> list[Account]:
        """
        Scans the directory for all account JSON files and returns a list of Account objects.
        Each account folder should contain a .json file with account details.
        """
        accounts = []

        for root, _, files in os.walk(SESSIONS_UPLOAD_DIR):
            for file in files:
                try:
                    if file.endswith('.json'):
                        json_path = os.path.join(root, file)

                        base_name = os.path.splitext(file)[0]
                        session_file = os.path.join(root, f"{base_name}.session")

                        if not os.path.isfile(session_file):
                            continue

                        with open(json_path, 'r') as json_file:
                            account_data = json.load(json_file)

                            account = Account(
                                session_file=session_file,
                                phone=account_data.get("phone"),
                                app_id=account_data.get("app_id"),
                                app_hash=account_data.get("app_hash"),
                                username=account_data.get("username")
                            )
                            accounts.append(account)
                except Exception as error:
                    logger.error(error)

        return accounts

    @staticmethod
    async def clear_cache():
        cache.clear()
