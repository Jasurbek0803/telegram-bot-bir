from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import back_button, user_main_menu
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


@router.message(F.text == "➕ Test Yaratish")
async def create_test(message: Message, state: FSMContext):
    user_id = message.from_user.id

    is_admin = await db.execute("SELECT 1 FROM admins WHERE user_id = $1", user_id, fetchval=True)
    is_superadmin = await db.execute("SELECT 1 FROM superadmins WHERE user_id = $1", user_id, fetchval=True)

    if not is_admin and not is_superadmin:
        await message.answer("❌ Siz admin emassiz!\n"
                             "Admin bo'lish uchun ushbu raqamga bog'laning: +998932244730")
        return

    await state.clear()

    await message.answer("📋 Test yaratish ma'lumotlarini kiriting\n"
                         "Format: maxsus_kod*javoblar*o'quv_markaz_nomi*test_egasi", reply_markup=back_button)
    await state.set_state(AdminStates.waiting_for_create_test_data)


@router.message(AdminStates.waiting_for_create_test_data)
async def input_test_data(message: Message, state: FSMContext):
    test_data = message.text.strip().split('*')
    if len(test_data) != 4:
        await message.answer("❗ Test ma'lumotlari noto'g'ri kiritildi. Ortga tugmasini bosing.\n\n"
                             "To'g'ri format: maxsus_kod*javoblar*o'quv_markaz_nomi*test_egasi")
        return

    maxsus_kod, javoblar, oquv_markaz, test_egasi = test_data

    # 🔐 Maxsus kodni raqamga aylantirish (agar kerak bo'lsa)
    try:
        maxsus_kod_int = int(maxsus_kod)
    except ValueError:
        await message.answer("❌ Maxsus kod faqat raqamlardan iborat bo'lishi kerak!")
        return

    # ❌ Takroriy kod tekshiruvi
    existing = await db.execute(
        "SELECT code FROM tests WHERE code = $1",
        maxsus_kod_int,
        fetchval=True
    )
    if existing:
        await message.answer(f"❌ Bu maxsus kod allaqachon mavjud: {maxsus_kod}")
        return

    # ✅ Testni bazaga qo‘shish
    try:
        await db.execute(
            """
            INSERT INTO tests (code, answers, center_name, author, author_id)
            VALUES ($1, $2, $3, $4, $5)
            """,
            maxsus_kod_int, javoblar, oquv_markaz, test_egasi, message.from_user.id,
            execute=True
        )

        await message.answer(f"✅ Test muvaffaqiyatli saqlandi:\n\n"
                             f"🔑 Maxsus kod: {maxsus_kod}\n"
                             f"🙈 Javoblar: {javoblar}\n"
                             f"🏫 O'quv markazi: {oquv_markaz}\n"
                             f"👤 Test egasi: {test_egasi}")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")

    await state.clear()
