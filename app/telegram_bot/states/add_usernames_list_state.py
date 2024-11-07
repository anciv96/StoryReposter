from aiogram.fsm.state import State, StatesGroup


# Определяем состояния
class AddUsernamesState(StatesGroup):
    file = State()
