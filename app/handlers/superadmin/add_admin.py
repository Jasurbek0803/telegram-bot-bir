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


async def add_admin_to_db(admin_id: int, full_name: str = ""):
    await db.add_admin(admin_id, full_name)


@router.message(F.text == "Admin Qo'shish")
async def add_admin(message: Message, state: FSMContext):
    if not await db.is_superadmin(message.from_user.id):
        await message.answer("❌ Siz superadmin emassiz.")
        return

    await message.answer("➕ Qo‘shmoqchi bo‘lgan adminning ID raqamini yuboring:")
    await state.set_state(AdminStates.waiting_for_admin_id)


@router.message(AdminStates.waiting_for_admin_id)
async def confirm_add_admin(message: Message, state: FSMContext, bot: Bot):
    try:
        admin_id = int(message.text.strip())
    except ValueError:
        await message.answer("❗ Iltimos, faqat sonlardan iborat ID yuboring.")
        await state.clear()
        return

    if await db.is_admin(admin_id):
        await message.answer("⚠️ Bu foydalanuvchi allaqachon admin.")
    else:
        try:
            chat = await bot.get_chat(admin_id)
            full_name = chat.full_name
        except Exception:
            await message.answer("❌ Foydalanuvchini topib bo‘lmadi. U botga /start yuborganiga ishonch hosil qiling.")
            await state.clear()
            return

        await add_admin_to_db(admin_id, full_name)
        await message.answer(f"✅ Foydalanuvchi {full_name} ({admin_id}) admin sifatida qo‘shildi.")

    await state.clear()
