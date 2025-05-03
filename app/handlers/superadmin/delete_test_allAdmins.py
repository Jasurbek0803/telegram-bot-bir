from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu
from app.states.admin import AdminStates
from app.utils.db import db  # asyncpg versiyasi


router = Router()


@router.message(F.text == "🔙 Ortga")
async def back(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if await db.is_superadmin(user_id):
        await state.clear()
        await message.answer("Superadmin bosh sahifasi", reply_markup=superadmin_menu)
    elif await db.is_admin(user_id):
        await state.clear()
        await message.answer("Admin bosh sahifa", reply_markup=admin_menu)
    else:
        await state.clear()
        await message.answer("Bosh sahifadasiz", reply_markup=user_main_menu)


@router.message(F.text == "🗑 Test O'chirish")
async def delete_test(message: Message, state: FSMContext):
    user_id = message.from_user.id

    admin_ids = await db.get_admin_ids()
    superadmin_ids = await db.get_superadmin_ids()

    if user_id not in admin_ids and user_id not in superadmin_ids:
        await message.answer("❌ Siz admin emassiz!\n"
                             "Admin bo'lish uchun ushbu raqamga bog'laning: +998932244730")
        return

    await message.answer("📋 O'chirish uchun testning maxsus kodini kiriting:")
    await state.set_state(AdminStates.waiting_for_test_code_to_delete)


@router.message(AdminStates.waiting_for_test_code_to_delete)
async def input_test_code_to_delete(message: Message, state: FSMContext):
    await state.clear()
    maxsus_kod = int(message.text.strip())
    user_id = message.from_user.id

    superadmin_ids = await db.get_superadmin_ids()
    is_superadmin = user_id in superadmin_ids

    # Testni o‘chirishga ruxsat berilganmi yoki yo‘qligini tekshirish
    success = await db.delete_test_if_allowed(code=maxsus_kod, user_id=user_id, is_superadmin=is_superadmin)

    if success:
        await message.answer(f"✅ Test (maxsus kod: {maxsus_kod}) muvaffaqiyatli o'chirildi.")
    else:
        await message.answer("❌ Siz bu testni o‘chira olmaysiz yoki test mavjud emas.")
