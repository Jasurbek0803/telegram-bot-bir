from aiogram.fsm.state import State, StatesGroup

class CreateTestStates(StatesGroup):
    waiting_for_test_data = State()
