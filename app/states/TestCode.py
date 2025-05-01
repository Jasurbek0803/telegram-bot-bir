from aiogram.fsm.state import StatesGroup, State


class TesCode(StatesGroup):
    waiting_test_code = State()