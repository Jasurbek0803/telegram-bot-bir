import re
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import contact_keyboard, user_main_menu, settings_in
from app.states.registration import RegistrationStates

from app.utils.database import Database  # <-- Database klassingiz joylashgan to'g'ri manzilni yozing

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


@router.message(F.text == "📋 Registratsiya")
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Iltimos, Ism-Familiyangizni kiriting:")
    await state.set_state(RegistrationStates.waiting_for_full_name)


@router.message(RegistrationStates.waiting_for_full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    words = full_name.split()
    if len(words) < 2:
        await message.answer("Iltimos, to'liq Ism-Familiyangizni kiriting (masalan: Jasur Karimov).")
        return
    for word in words:
        if not re.match(r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ'ʼʻ’‘-]+$", word):
            await message.answer("Ism-Familiyada faqat harflardan foydalaning")
            return

    await state.update_data(full_name=full_name)
    await message.answer("Endi raqamingizni pastdagi tugmani bosish orqali yuboring⬇️", reply_markup=contact_keyboard)
    await state.set_state(RegistrationStates.waiting_for_phone_number)


@router.message(RegistrationStates.waiting_for_phone_number)
async def get_phone_number(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer("Iltimos, pastdagi tugmadan foydalanib raqamingizni yuboring")
        await state.clear()
        return

    user_data = await state.get_data()
    full_name = user_data.get("full_name")
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ma'lumotlarni SQLite bazaga saqlash
    db.add_user(user_id=user_id, full_name=full_name, phone=phone_number)

    await state.clear()
    await message.answer(
        f"Ma'lumotlaringiz qabul qilindi!\n\n"
        f"👤 Ism-Familiya: {full_name}\n"
        f"📞 Telefon raqam: {phone_number}",
        reply_markup=user_main_menu
    )


@router.message(F.text == "⚙️ Sozlamalar")
async def edit_registration(message: Message, state: FSMContext):
    await message.answer("🛠 Kerakli bo'limni tanlang",reply_markup=settings_in)


@router.message(F.text == "🔄 Shaxsiy ma'lumotlarni o'zgartirish 🔄")
async def edit_registration(message: Message, state: FSMContext):
    await message.answer("✍️ Qayta ism-familiyangizni kiriting.\n\n"
                         "Masalan: Ali Valiyev")
    await state.set_state(RegistrationStates.waiting_for_full_name)

