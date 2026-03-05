from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu
from app.states.admin import AdminStates
from app.utils.db import db

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

@router.message(F.text == "👥 Foydalanuvchilar soni")
async def get_user_count(message: Message):
    print("🚀 Handler ishga tushdi!")  # test uchun
    user_count = await db.execute("SELECT COUNT(*) FROM users;", fetchval=True)
    await message.answer(f"📊 Botdagi jami foydalanuvchilar soni: <b>{user_count}</b>", parse_mode="HTML")
