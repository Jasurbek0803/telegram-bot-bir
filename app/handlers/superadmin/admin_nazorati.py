from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu, nazorat
from app.keyboards.user import user_main_menu
from app.states.admin import AdminStates
from app.utils.database import Database


router = Router()
db = Database()

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





@router.message(F.text == "Admin Nazorati")
async def admin_nazorat(message: Message, state: FSMContext):
    if not db.is_superadmin(message.from_user.id):
        await message.answer("❌ Siz superadmin emassiz.")
        return

    await message.answer("Kerakli bo'limni tanlang", reply_markup=nazorat)


@router.message(F.text == "Kimlar Admin")
async def admin_nazorat(message: Message, state: FSMContext):
    # Faqat superadminlar uchun ruxsat
    if not db.is_superadmin(message.from_user.id):
        await message.answer("❌ Siz superadmin emassiz.")
        return

    # Barcha admin IDlarini olish
    admin_ids = db.get_admin_ids()
    if not admin_ids:
        await message.answer("📭 Hozircha hech qanday admin mavjud emas.")
        return

    # Har bir admin haqida to'liq ma'lumotlarni olish
    text = "📋 *Adminlar ro'yxati:*\n\n"
    for idx, admin_id in enumerate(admin_ids, start=1):
        user = db.get_user_by_id(admin_id)
        if user:
            full_name = user[1]  # 0: user_id, 1: full_name, 2: phone, 3: registered_at
            phone = user[2]
            text += f"{idx}. 👤 {full_name} | 📞 {phone} | 🆔 {admin_id}\n"
        else:
            text += f"{idx}. ⚠️ Ma'lumot topilmadi | 🆔 {admin_id}\n"

    await message.answer(text, parse_mode="Markdown")




