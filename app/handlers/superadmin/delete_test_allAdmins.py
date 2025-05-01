from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu
from app.states.admin import AdminStates
from app.utils.database import Database


db = Database()
router = Router()
@router.message(F.text == "🔙 Ortga")
async def back(message: Message, state: FSMContext):
    id = message.from_user.id

    if db.is_superadmin(int(id)):
        await state.clear()
        await message.answer("Superadmin bosh sahifasi ",reply_markup=superadmin_menu)
        return
    elif db.is_admin(int(id)):
        await state.clear()
        await message.answer("Admin bosh sahifa", reply_markup=admin_menu)
        return
    else:
        await state.clear()
        await message.answer("Bosh sahifadasiz",reply_markup=user_main_menu)
        return

@router.message(F.text == "🗑 Test O'chirish")
async def delete_test(message: Message, state: FSMContext):
    user_id = message.from_user.id


    admin_ids = db.get_admin_ids()
    superadmin_ids = db.get_superadmin_ids()

    if user_id not in admin_ids and user_id not in superadmin_ids:
        await message.answer("❌ Siz admin emassiz!\n"
                             "Admin bo'lish uchun ushbu raqamga bog'laning: +998932244730")
        return

    await message.answer("📋 O'chirish uchun testning maxsus kodini kiriting:")
    await state.set_state(AdminStates.waiting_for_test_code_to_delete)

@router.message(AdminStates.waiting_for_test_code_to_delete)
async def input_test_code_to_delete(message: Message, state: FSMContext):
    await state.clear()
    maxsus_kod = message.text.strip()
    user_id = message.from_user.id

    # Admin va superadminlar ro'yxati
    superadmin_ids = db.get_superadmin_ids()
    is_superadmin = user_id in superadmin_ids

    # Testni o'chirishga ruxsat berilganmi tekshiramiz
    success = db.delete_test_if_allowed(code=int(maxsus_kod), user_id=user_id, is_superadmin=is_superadmin)

    if success:

        await message.answer(f"✅ Test (maxsus kod: {maxsus_kod}) muvaffaqiyatli o'chirildi.")

    else:
        await message.answer(f"❌ Siz bu testni o‘chira olmaysiz yoki test mavjud emas.")
