from aiogram.fsm.state import State, StatesGroup

class SolveTestStates(StatesGroup):
    waiting_for_test_code = State()
    waiting_for_answers = State()
