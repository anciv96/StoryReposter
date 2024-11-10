from aiogram import F, Router
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app import logger_setup
from app.telegram_bot.filters.admin_filter import IsAdminFilter
from app.telegram_bot.keyboards.default.menu_keyboard import menu_kb
from app.telegram_bot.keyboards.default.settings_keyboard import cancel_kb
from app.telegram_bot.states.settings_state import AdminsListState
from config.config import ConfigManager, OWNER

logger = logger_setup.get_logger(__name__)
admins_list_router = Router(name=__name__)


@admins_list_router.message(
    and_f(
        F.text == 'Посмотреть список админов',
        IsAdminFilter(True)
    )
)
async def show_admins_list_handler(message: Message) -> None:
    if message.from_user.id == OWNER:
        message_text = f'Админы: \n'
        admins = await ConfigManager.get_setting('admins_ids')
        for admin in admins:
            message_text += f'{admin}\n'
        await message.answer(message_text)


@admins_list_router.message(
    and_f(
        F.text == 'Изменить список админов',
        IsAdminFilter(True)
    )
)
async def change_admins_list_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id == OWNER:
        await message.answer('Введите список админов через 1 пробел (старые админы будут удалены):',
                             reply_markup=cancel_kb)
        await state.set_state(AdminsListState.admins)


@admins_list_router.message(AdminsListState.admins)
async def get_period_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.text == 'Отмена':
        await message.answer('Отмена действия.', reply_markup=menu_kb)

    else:
        admins = [int(admin) for admin in message.text.split(' ')]
        await ConfigManager.set_setting(key='admins_ids', value=admins)
        await message.answer(f'Админы сохранены!',
                             reply_markup=menu_kb)


async def _convert_admin_list(message: Message):
    valid_result = []
    admins = message.text.split(' ')
    for admin in admins:
        try:
            valid_result.append(int(admin))
        except ValueError:
            await message.answer(f'Ошибка {admin}. id админа должен быть числом.', reply_markup=menu_kb)
