from aiogram.fsm.state import StatesGroup, State


class ImportAccount(StatesGroup):
    archive_file = State()
    proxy_file = State()
