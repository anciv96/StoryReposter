from aiogram import F, Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.states.settings_state import TagsState
from config.config import ConfigManager

logger = logger_setup.get_logger(__name__)
tags_settings_router = Router(name=__name__)


@tags_settings_router.message(and_f(
    F.text == 'Количество отметок с одного аккаунта',
    IsAdminFilter(True)
))
async def tags_handler(message: Message, state: FSMContext) -> None:
    await message.answer('Укажите количество отметок, которое будет выполняться с 1-го аккаунта', reply_markup=menu_kb)
    await state.set_state(TagsState.tags_quantity)


@tags_settings_router.message(TagsState.tags_quantity)
async def get_tags_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        tags_quantity = int(message.text)
    except ValueError:
        await message.answer('Количество должно быть целым числом.', reply_markup=menu_kb)
        return

    await ConfigManager.set_setting(key='tags_per_story', value=tags_quantity)
    await message.answer(f'Количество отметок с одного аккаунта установлено {tags_quantity}',
                         reply_markup=menu_kb)
