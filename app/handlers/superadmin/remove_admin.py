from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states.admin import AdminStates
from app.utils.database import Database


router = Router()
db = Database()

@router.message(F.text == "Adminni O'chirish")
async def remove_admin(message: Message, state: FSMContext):
    # superadminlikni database orqali tekshiramiz
    superadmin = db.execute(
        "SELECT 1 FROM superadmins WHERE user_id = ?",
        parameters=(message.from_user.id,),
        fetchone=True
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
        await state.clear()
        return

    admin_exists = db.execute(
        "SELECT 1 FROM admins WHERE user_id = ?",
        parameters=(admin_id,),
        fetchone=True
    )

    if not admin_exists:
        await message.answer("⚠️ Bu foydalanuvchi admin emas.")
    else:
        db.execute(
            "DELETE FROM admins WHERE user_id = ?",
            parameters=(admin_id,),
            commit=True
        )
        await message.answer(f"✅ Foydalanuvchi {admin_id} adminlar ro‘yxatidan o‘chirildi.")

    await state.clear()
