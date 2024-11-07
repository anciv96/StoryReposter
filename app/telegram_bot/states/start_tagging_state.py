from aiogram.fsm.state import StatesGroup, State


class StartTaggingState(StatesGroup):
    donor_account = State()
