from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu, nazorat
from app.keyboards.user import user_main_menu
from app.states.admin import AdminStates
from app.utils.db import db  # Asosiy o‘zgartirish shu yerda

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


@router.message(F.text == "Admin Nazorati")
async def admin_nazorat(message: Message, state: FSMContext):
    if not await db.is_superadmin(message.from_user.id):
        await message.answer("❌ Siz superadmin emassiz.")
        return

    await message.answer("Kerakli bo'limni tanlang", reply_markup=nazorat)


@router.message(F.text == "Kimlar Admin")
async def kimlar_admin(message: Message, state: FSMContext):
    if not await db.is_superadmin(message.from_user.id):
        await message.answer("❌ Siz superadmin emassiz.")
        return

    admin_ids = await db.get_admin_ids()
    if not admin_ids:
        await message.answer("📭 Hozircha hech qanday admin mavjud emas.")
        return

    text = "📋 *Adminlar ro'yxati:*\n\n"
    for idx, admin_id in enumerate(admin_ids, start=1):
        user = await db.get_user_by_id(admin_id)
        if user:
            full_name = user["full_name"]
            phone = user["phone"]
            text += f"{idx}. 👤 {full_name} | 📞 {phone} | 🆔 {admin_id}\n"
        else:
            text += f"{idx}. ⚠️ Ma'lumot topilmadi | 🆔 {admin_id}\n"

    await message.answer(text, parse_mode="Markdown")
