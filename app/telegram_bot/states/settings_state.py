from aiogram.fsm.state import StatesGroup, State


class PeriodState(StatesGroup):
    period = State()


class PostingDelayState(StatesGroup):
    delay = State()


class TagsState(StatesGroup):
    tags_quantity = State()


class AdminsListState(StatesGroup):
    admins = State()


