from aiogram.fsm.state import StatesGroup, State

class Reklama(StatesGroup):
    waiting_for_reklama = State()