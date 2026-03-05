from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states.admin import AdminStates
from app.utils.db import db # asyncpg bilan mos klass

router = Router()


@router.message(F.text == "Adminni O'chirish")
async def remove_admin(message: Message, state: FSMContext):
    # Superadminlikni tekshirish
    superadmin = await db.execute(
        "SELECT 1 FROM superadmins WHERE user_id = $1",
        message.from_user.id,
        fetch=True
    )

    if not superadmin:
        await message.answer("❌ Siz superadmin emassiz.")
        return

    await message.answer("➖ O'chirmoqchi bo‘lgan adminning ID raqamini yuboring:")
    await state.set_state(AdminStates.waiting_for_admin_id_remove)



@router.message(AdminStates.waiting_for_admin_id_remove)
async def confirm_remove_admin(message: Message, state: FSMContext):
    try:
        admin_id = int(message.text.strip())
    except ValueError:
        await message.answer("❗ Iltimos, faqat sonlardan iborat ID yuboring.")
        return

    admin_exists = await db.execute(
        "SELECT 1 FROM admins WHERE user_id = $1",
        admin_id,fetchrow=True
    )

    if not admin_exists:
        await message.answer("⚠️ Bu foydalanuvchi admin emas.")
    else:
        await db.execute(
            "DELETE FROM admins WHERE user_id = $1",
            admin_id,execute=True

        )
        await message.answer(f"✅ Foydalanuvchi {admin_id} adminlar ro‘yxatidan o‘chirildi.")

    await state.clear()
