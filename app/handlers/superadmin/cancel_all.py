from aiogram import Router,F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.admin import admin_menu
from app.states.admin import AdminStates

router = Router()

@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Siz hech qanday jarayonda emassiz.", reply_markup=admin_menu)
    elif current_state == AdminStates.waiting_for_admin_id:
        await state.clear()
        await message.answer("✅ Jarayon bekor qilindi. Siz asosiy menyudasiz.", reply_markup=admin_menu)
    elif current_state == AdminStates.waiting_for_test_data:
        await state.clear()
        await message.answer("✅ Jarayon bekor qilindi. Siz asosiy menyudasiz.", reply_markup=admin_menu)
    elif current_state == AdminStates.waiting_for_test_code_to_delete:
        await state.clear()
        await message.answer("✅ Jarayon bekor qilindi. Siz asosiy menyudasiz.", reply_markup=admin_menu)
