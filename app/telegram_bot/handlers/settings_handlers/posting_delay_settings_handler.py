from aiogram import F, Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.states.settings_state import PostingDelayState
from config.config import ConfigManager

logger = logger_setup.get_logger(__name__)
posting_delay_settings_router = Router(name=__name__)


@posting_delay_settings_router.message(and_f(
    F.text == 'Задержка между постингом',
    IsAdminFilter(True)
))
async def delay_handler(message: Message, state: FSMContext) -> None:
    await message.answer('Введите задержу между постингом сторис в секундах', reply_markup=menu_kb)
    await state.set_state(PostingDelayState.delay)


@posting_delay_settings_router.message(PostingDelayState.delay)
async def get_delay_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        delay = int(message.text)
    except ValueError:
        await message.answer('Задержка должна быть целым числом.', reply_markup=menu_kb)
        return

    await ConfigManager.set_setting(key='posting_delay', value=delay)
    await message.answer(f'Вы успешно установили время {delay}', reply_markup=menu_kb)
