import ssl
from typing import Any, Optional

import aiohttp
import aiofiles
import python_socks
from aiohttp_socks import ProxyConnector

from app import logger_setup
from app.exceptions.account_exceptions import ProxyIsNotValidError
from app.utils.folder_utils import get_txt_file_path, get_txt_file_or_create
from config.config import PROXIES_UPLOAD_DIR


logger = logger_setup.get_logger(__name__)


async def convert_proxy(proxy_input: str) -> Optional[dict[str, Any]]:
    """
    Parses the proxy input string and returns a proxy tuple if valid.
    If proxy input is '-', returns None for no proxy.
    """
    try:
        if proxy_input is None:
            return None
        proxy_parts = proxy_input.split(':')

        return {
            'proxy_type': python_socks.ProxyType.SOCKS5,
            'addr': proxy_parts[0],
            'port': int(proxy_parts[1]),
            'username': proxy_parts[2],
            'password': proxy_parts[3],
            'rdns': True,
        }
    except (IndexError, ValueError):
        raise ProxyIsNotValidError("Неправильный формат прокси. Ожидалось host:port:login:password.")


async def parse_proxy() -> Optional[list[str]]:
    file_path = await get_txt_file_path(PROXIES_UPLOAD_DIR)

    async with aiofiles.open(file_path, mode='r') as file:
        source = await file.read()
        proxies = source.split('\n')

    valid_proxies = []
    for proxy in proxies:
        if proxy == '':
            continue

        try:
            valid_proxies.append(proxy)
        except (ValueError, IndexError):
            continue

    return valid_proxies


async def add_proxy(proxy: str):
    try:
        file_path = await get_txt_file_or_create(PROXIES_UPLOAD_DIR, 'proxies.txt')

        async with aiofiles.open(file_path, mode='a') as f:
            await f.write(f"\n{proxy}\n")
    except Exception as error:
        logger.error(error)


async def check_proxy(proxy_info: dict[str, Any]) -> None:
    if proxy_info == '' or proxy_info is None:
        return

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with aiohttp.ClientSession(connector=ProxyConnector(
                proxy_type=proxy_info['proxy_type'],
                host=proxy_info['addr'],
                port=proxy_info['port'],
                username=proxy_info['username'],
                password=proxy_info['password'],
                rdns=proxy_info['rdns'],
                ssl=ssl_context
        )) as session:
            resp = await session.get("https://google.com")
            resp.close()
            if resp.status != 200:
                raise ProxyIsNotValidError(f"Proxy {proxy_info['addr']} is not valid")
    except ProxyIsNotValidError as error:
        logger.error(error)
    except Exception as error:
        logger.error(error)
