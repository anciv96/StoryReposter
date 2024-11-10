from aiogram import F, Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.keyboards.default.settings_keyboard import story_period_kb
from app.telegram_bot.states.settings_state import PeriodState
from config.config import ConfigManager

logger = logger_setup.get_logger(__name__)
period_settings_router = Router(name=__name__)


@period_settings_router.message(and_f(
    F.text == 'Время нахождения сторис в профиле',
    IsAdminFilter(True)
))
async def period_handler(message: Message, state: FSMContext) -> None:
    await message.answer('Выберите период:', reply_markup=story_period_kb)
    await state.set_state(PeriodState.period)


@period_settings_router.message(PeriodState.period)
async def get_period_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    period = message.text
    if period == '6 часов':
        period = 6
    elif period == '12 часов':
        period = 12
    elif period == '24 часа':
        period = 24
    else:
        period = 48

    await ConfigManager.set_setting(key='story_period', value=period)
    await message.answer(f'Время нахождения сторис в профиле {period}-часов', reply_markup=menu_kb)
