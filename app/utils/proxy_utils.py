from typing import Any, Optional

import aiofiles
import python_socks

from app import logger_setup
from app.exceptions.account_exceptions import ProxyIsNotValidError
from app.utils.folder_utils import get_txt_file_path, get_txt_file_or_create
from config.config import PROXIES_UPLOAD_DIR


logger = logger_setup.get_logger(__name__)


async def convert_proxy(proxy_input: str) -> dict[str, Any]:
    """
    Parses the proxy input string and returns a proxy tuple if valid.
    If proxy input is '-', returns None for no proxy.
    """
    try:
        proxy_parts = proxy_input.split(':')
        return {
            'proxy_type': python_socks.ProxyType.SOCKS5,
            'addr': proxy_parts[0],
            'port': int(proxy_parts[1]),
            'username': proxy_parts[2],
            'password': proxy_parts[3],
            'rdns': False,
        }
    except (IndexError, ValueError):
        raise ProxyIsNotValidError("Неправильный формат прокси. Ожидалось host:port:login:password.")


async def parse_proxy() -> Optional[list[dict[str, Any]]]:
    file_path = await get_txt_file_path(PROXIES_UPLOAD_DIR)

    async with aiofiles.open(file_path, mode='r') as file:
        source = await file.read()
        proxies = source.split('\n')

    valid_proxies = []
    for proxy in proxies:
        if proxy == '':
            continue

        try:
            valid_proxies.append(await convert_proxy(proxy))
        except (ValueError, IndexError):
            continue

    return valid_proxies


async def add_proxy(proxy: str):
    try:
        file_path = await get_txt_file_or_create(PROXIES_UPLOAD_DIR, 'proxies.txt')

        async with aiofiles.open(file_path, mode='a') as f:
            await f.write(f"{proxy}\n")
    except Exception as error:
        logger.error(error)
