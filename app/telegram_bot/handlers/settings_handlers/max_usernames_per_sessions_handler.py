from aiogram import F, Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.states.settings_state import MaxUsernamesState
from config.config import ConfigManager

logger = logger_setup.get_logger(__name__)
max_usernames_router = Router(name=__name__)


@max_usernames_router.message(and_f(
    F.text == 'Максимальное количество отметок с одного аккаунта',
    IsAdminFilter(True)
))
async def max_usernames_handler(message: Message, state: FSMContext) -> None:
    await message.answer('Укажите количество отметок, которое будет выполняться с 1-го аккаунта', reply_markup=menu_kb)
    await state.set_state(MaxUsernamesState.max_tags_quantity)


@max_usernames_router.message(MaxUsernamesState.max_tags_quantity)
async def get_max_usernames_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    tags_per_story = await ConfigManager.get_setting('tags_per_story')
    try:
        max_tags_quantity = int(message.text)
        if max_tags_quantity < 1 or max_tags_quantity < tags_per_story:
            raise ValueError
    except ValueError:
        await message.answer(f'Количество должно быть целым числом. Большим чем {tags_per_story}', reply_markup=menu_kb)
        return

    await ConfigManager.set_setting(key='max_usernames_per_session', value=max_tags_quantity)
    await message.answer(f'Максимальное количество отметок с одного аккаунта установлено '
                         f'{max_tags_quantity}', reply_markup=menu_kb)
