from aiogram.fsm.state import State, StatesGroup


# Определяем состояния
class AddAccountState(StatesGroup):
    phone = State()
    api_id = State()
    api_hash = State()
    proxy = State()
    code = State()
    two_fa_password = State()
