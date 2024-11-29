from random import uniform

import asyncio

from aiogram import Router, F
from aiogram.filters import Command, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import logger_setup
from app.backend.schemas.account import Account
from app.backend.services.account_service import AccountService
from app.backend.services.story_services.download_story_service import DownloadStoryService
from app.backend.services.story_services.post_story_service import PostStoryService
from app.exceptions.account_exceptions import NotAuthenticatedError, ProxyIsNotValidError
from app.exceptions.story_exceptions import NoActiveStoryError
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.states.start_tagging_state import StartTaggingState
from app.utils.folder_utils import get_usernames, clear_directory, get_first_media_file
from app.utils.proxy_utils import parse_proxy
from config.config import USERNAMES_LIST_DIR, LAST_STORY_CONTENT_DIR, ConfigManager

start_tagging_router = Router(name=__name__)
logger = logger_setup.get_logger(__name__)


@start_tagging_router.message(and_f(
    or_f(
        Command('start_tagging'),
        F.text == '▶️ Начать теггинг'),
    IsAdminFilter(True)
))
async def request_donor_account(message: Message, state: FSMContext):
    await ConfigManager.set_setting('turned_on', True)

    await message.reply("Введите номер телефона или @username аккаунта-донора, на котором должна быть активная сторис.")
    await state.set_state(StartTaggingState.donor_account)


@start_tagging_router.message(StartTaggingState.donor_account)
async def set_donor_account(message: Message, state: FSMContext):
    await message.answer('Обработка...')
    await state.clear()
    donor_account = message.text
    await start_tagging_process(message, donor_account)


async def start_tagging_process(message: Message, donor_account):
    await AccountService.clear_cache()
    sessions = await AccountService.get_all_accounts()

    if len(sessions) == 0:
        await message.answer('Нет активных пользователей.')
        return

    try:
        proxy_groups = await parse_proxy()
        session_proxy = sessions[0].proxy
        if session_proxy is None:
            if proxy_groups:
                session_proxy = proxy_groups[0]
    except FileNotFoundError:
        await message.answer('Прокси не найдены.')
        return

    try:
        service = DownloadStoryService()
        await clear_directory(LAST_STORY_CONTENT_DIR)
        await service.download_last_story(
            donor_account,
            sessions[0],
            proxy_input=session_proxy,
        )
        await message.reply(f"Аккаунт-донор успешно добавлен: {donor_account}", )

        await message.reply("Запуск процесса теггинга...", reply_markup=menu_kb)
        await post_stories_for_all_sessions(sessions, proxy_groups)

    except NoActiveStoryError:
        await message.answer('У пользователя нет активных историй.')
    except ProxyIsNotValidError as error:
        logger.error(error)
    except NotAuthenticatedError:
        await message.answer(f'Ошибка скачивания сторис. {sessions[0].phone}')
    except ValueError:
        await message.answer(f'Пользователь {donor_account} не найден')


async def post_stories_for_all_sessions(sessions: list[Account], proxy_groups: list[str]) -> None:
    try:
        usernames = await get_usernames(USERNAMES_LIST_DIR)

        grouped_by_proxy = {}
        for i, session in enumerate(sessions):
            proxy = proxy_groups[i % len(proxy_groups)] if proxy_groups else None

            if proxy not in grouped_by_proxy:
                grouped_by_proxy[proxy] = []
            grouped_by_proxy[proxy].append(session)

        tasks = []
        for proxy, sessions in grouped_by_proxy.items():
            task = asyncio.create_task(post_stories_for_sessions_with_proxy(proxy, sessions, usernames))
            tasks.append(task)

        await asyncio.gather(*tasks)

    except FileNotFoundError:
        logger.error('Файл с юзернеймами не найден')
    except Exception as error:
        logger.error(f"Произошла ошибка: {error}")


async def post_stories_for_sessions_with_proxy(proxy, sessions, usernames):

    try:
        grouped_usernames = await _get_grouped_usernames(usernames)
        tasks = await _get_post_stories_tasks(proxy, sessions, grouped_usernames)

        for task in asyncio.as_completed(tasks):
            await task
            await asyncio.sleep(uniform(0.5, 1))

    except IndexError:
        logger.error("Недостаточно юзернеймов для постинга сторис")
    except Exception as error:
        logger.error(f"Ошибка при обработке сессий с прокси: {error}")


async def _get_grouped_usernames(usernames) -> list[list[str]]:
    max_usernames_per_session = await ConfigManager.get_setting('max_usernames_per_session')

    grouped_usernames = []
    for i in range(0, len(usernames), max_usernames_per_session):
        try:
            grouped_usernames.append(usernames[i:i + max_usernames_per_session])
        except IndexError:
            break

    return grouped_usernames


async def _get_post_stories_tasks(proxy, sessions, usernames) -> list:
    story_service = PostStoryService()

    tasks = []
    for i, session in enumerate(sessions):
        tasks.append(
            story_service.post_story_with_tags(
                session,
                story=await get_first_media_file(),
                tags=usernames[i],
                proxy=proxy
            )
        )
    return tasks
