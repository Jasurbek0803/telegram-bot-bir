from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu, back_button
from app.states.reklama import Reklama

from app.utils.database import Database


router = Router()
db = Database()


@router.message(F.text == "🔙 Ortga")
async def back(message: Message, state: FSMContext):
    id = message.from_user.id

    if db.is_superadmin(int(id)):
        await state.clear()
        await message.answer("Superadmin bosh sahifasi", reply_markup=superadmin_menu)
    elif db.is_admin(int(id)):
        await state.clear()
        await message.answer("Admin bosh sahifa", reply_markup=admin_menu)
    else:
        await state.clear()
        await message.answer("Bosh sahifadasiz", reply_markup=user_main_menu)

@router.message(F.text == "📢 Reklama yuborish")
async def ask_for_ad_text(message: Message, state: FSMContext):
    if not db.is_superadmin(message.from_user.id):
        await message.answer("❌ Siz superadmin emassiz.")
        return
    await message.answer("📨 Yubormoqchi bo‘lgan reklamani matnini kiriting (yoki rasm, video bilan yuboring):",reply_markup=back_button)
    await state.set_state(Reklama.waiting_for_reklama)


@router.message(Reklama.waiting_for_reklama)
async def broadcast_ad(message: Message, state: FSMContext, bot: Bot):
    users = db.get_all_user_id()
    count = 0
    for user in users:
        user_id = user[0]
        try:
            # Reklama matn, rasm, video — qanday bo‘lsa ham yuboriladi
            if message.text:
                await bot.send_message(user_id, message.text)
            elif message.photo:
                await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await bot.send_video(user_id, message.video.file_id, caption=message.caption or "")
            count += 1
        except:
            continue

    await message.answer(f"✅ Reklama {count} foydalanuvchiga yuborildi.")
    await state.clear()
