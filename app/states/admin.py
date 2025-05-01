from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    waiting_for_create_test_data = State()
    waiting_for_admin_id_remove = State()
    waiting_for_admin_id = State()
    waiting_for_test_data = State()
    waiting_for_test_code_to_delete = State()
    waiting_for_cancel = State()