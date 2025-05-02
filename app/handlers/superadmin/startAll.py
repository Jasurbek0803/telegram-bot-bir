import logging
from aiogram import Router, F
from aiogram.types import Message
from app.keyboards.admin import registration_admin, admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import registrationUser, user_main_menu
from app.utils.database import Database


router = Router()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Database connection
db = Database()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id

    # Check if user exists in the database
    user = db.get_user_by_id(user_id)

    # If user exists, retrieve the full name
    if user:
        full_name = user[1]  # Assuming full_name is the second column in users table
        found = True
    else:
        found = False
        full_name = ""

    # Load admin and superadmin IDs from the database
    admin_data = db.execute("SELECT user_id FROM admins;", fetchall=True)
    superadmin_data = db.execute("SELECT user_id FROM superadmins;", fetchall=True)

    admin_id = [x[0] for x in admin_data]
    superadmin_id = [x[0] for x in superadmin_data]

    if user_id in superadmin_id:
        await message.answer("Super Admin menuga xush kelibsiz! ", reply_markup=superadmin_menu)
    elif user_id in admin_id:
        await message.answer("Admin menuga xush kelibsiz! ", reply_markup=admin_menu)
    elif found:
        await message.answer(f"Xush kelibsiz, {full_name}! 👋", reply_markup=user_main_menu)
    else:
        # If the user is not registered, ask for registration
        await message.answer(
            f"Assalomu alaykum, {message.from_user.full_name}!.\n\n"
            f"Botdan foydalanish uchun Registratsiya tugmasini bosing:",
            reply_markup=registrationUser
        )

    # If the user is not registered, insert them into the database
    if not found:
        db.add_user(user_id, message.from_user.full_name, message.from_user.phone_number)
