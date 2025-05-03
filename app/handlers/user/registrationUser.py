import re
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import Contact

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import contact_keyboard, user_main_menu, settings_in
from app.states.registration import RegistrationStates
from app.utils.db import db

router = Router()



@router.message(F.text == "📋 Registratsiya")
async def registration_entry(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if await db.is_superadmin(user_id):
        await state.clear()
        await message.answer("🔑 Superadmin bosh sahifasi", reply_markup=superadmin_menu)
    elif await db.is_admin(user_id):
        await state.clear()
        await message.answer("🛠 Admin bosh sahifa", reply_markup=admin_menu)
    else:
        await state.clear()
        await message.answer("👤 Ro‘yxatdan o‘tish uchun ism-familiyangizni kiriting:")
        await state.set_state(RegistrationStates.waiting_for_full_name)


@router.message(RegistrationStates.waiting_for_full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    words = full_name.split()
    if len(words) < 2:
        await message.answer("Iltimos, to‘liq ism-familiyangizni kiriting (masalan: Jasur Karimov).")
        return
    for word in words:
        if not re.match(r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ'ʼʻ’‘-]+$", word):
            await message.answer("Ism-familiyada faqat harflardan foydalaning.")
            return

    await state.update_data(full_name=full_name)
    await message.answer("📞 Endi telefon raqamingizni yuboring. Pastdagi tugmani bosing ⬇️",
                         reply_markup=contact_keyboard)
    await state.set_state(RegistrationStates.waiting_for_phone_number)


@router.message(RegistrationStates.waiting_for_phone_number, F.contact)
async def get_phone_number(message: Message, state: FSMContext):
    contact: Contact = message.contact
    user_data = await state.get_data()
    full_name = user_data.get("full_name")
    phone_number = contact.phone_number
    user_id = message.from_user.id

    await db.add_user(user_id=user_id, full_name=full_name, phone=phone_number)

    await state.clear()
    await message.answer(
        f"✅ Ma'lumotlaringiz saqlandi!\n\n"
        f"👤 Ism-familiya: {full_name}\n"
        f"📞 Telefon raqam: {phone_number}",
        reply_markup=user_main_menu
    )


@router.message(RegistrationStates.waiting_for_phone_number)
async def phone_number_error(message: Message):
    await message.answer("❗️ Iltimos, kontakt tugmasidan foydalanib raqamingizni yuboring.")


@router.message(F.text == "⚙️ Sozlamalar")
async def edit_settings(message: Message, state: FSMContext):
    await message.answer("🛠 Kerakli bo‘limni tanlang", reply_markup=settings_in)


@router.message(F.text == "🔄 Shaxsiy ma'lumotlarni o'zgartirish 🔄")
async def update_full_name(message: Message, state: FSMContext):
    await message.answer("✍️ Yangi ism-familiyangizni kiriting.\n\n"
                         "Masalan: Ali Valiyev")
    await state.set_state(RegistrationStates.waiting_for_full_name)
