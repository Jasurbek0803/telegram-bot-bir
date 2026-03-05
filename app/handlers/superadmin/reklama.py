from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu, back_button
from app.states.reklama import Reklama
from app.utils.db import db # async versiyasi

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


@router.message(F.text == "📢 Reklama yuborish")
async def ask_for_ad_text(message: Message, state: FSMContext):
    if not await db.is_superadmin(message.from_user.id):
        await message.answer("❌ Siz superadmin emassiz.")
        return
    await message.answer("📨 Yubormoqchi bo‘lgan reklamani matnini kiriting (yoki rasm, video bilan yuboring):",
                         reply_markup=back_button)
    await state.set_state(Reklama.waiting_for_reklama)


@router.message(Reklama.waiting_for_reklama)
async def broadcast_ad(message: Message, state: FSMContext, bot: Bot):
    users = await db.get_all_user_id()  # list of tuples [(id,), (id,), ...]
    count = 0

    for user in users:
        user_id = user[0]
        try:
            if message.text:
                await bot.send_message(user_id, message.text)
            elif message.photo:
                await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await bot.send_video(user_id, message.video.file_id, caption=message.caption or "")
            count += 1
        except:
            continue  # foydalanuvchi bloklagan bo‘lishi mumkin

    await message.answer(f"✅ Reklama {count} foydalanuvchiga yuborildi.")
    await state.clear()
