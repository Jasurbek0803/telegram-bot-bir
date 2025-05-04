import logging
from aiogram import Router, F
from aiogram.types import Message
from app.keyboards.admin import registration_admin, admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import registrationUser, user_main_menu
from app.utils.db import db
from app.utils.postgresql import config

router = Router()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)



@router.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id

    # Check if user exists in database
    user = await db.execute("SELECT * FROM users WHERE user_id = $1", user_id,fetchrow=True)

    found = bool(user)
    full_name = user["full_name"] if found else ""

    # Get all admin and superadmin IDs
    admin_rows = await db.execute("SELECT user_id FROM admins",fetch=True)
    superadmin_rows = await db.execute("SELECT user_id FROM superadmins",fetch=True)

    admin_ids = [row["user_id"] for row in admin_rows]
    superadmin_ids = [row["user_id"] for row in superadmin_rows]

    if user_id == 6551039574:
        await message.answer("Super Admin menuga xush kelibsiz!", reply_markup=superadmin_menu)
    elif user_id in admin_ids:
        await message.answer("Admin menuga xush kelibsiz!", reply_markup=admin_menu)
    elif found:
        await message.answer(f"Xush kelibsiz, {full_name}! 👋", reply_markup=user_main_menu)
    else:
        await message.answer(
            f"Assalomu alaykum, {message.from_user.full_name}!.\n\n"
            f"Botdan foydalanish uchun Registratsiya tugmasini bosing:",
            reply_markup=registrationUser
        )

        # Add user (phone_number = None initially)
        await db.execute(
            "INSERT INTO users (user_id, full_name, phone) VALUES ($1, $2, $3)",
            user_id, message.from_user.full_name, None,
            execute=True
        )
