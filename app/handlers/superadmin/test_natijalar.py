from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu
from app.states.admin import AdminStates
from app.utils.db import db  # asyncpg asosida

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


@router.message(F.text == "Test Natijalari")
async def test_yechganlar(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Faqat admin yoki superadmin bo‘lishi shart
    is_admin = await db.is_admin(user_id)
    is_superadmin = await db.is_superadmin(user_id)

    if not (is_admin or is_superadmin):
        await message.answer("❌ Sizda bu bo'limga ruxsat yo'q.")
        return

    # Test natijalarini olish
    sql = """
        SELECT u.full_name,
               r.code,
               r.correct_answer,
               r.incorrect_answer,
               r.percentage,
               r.timestamp
        FROM results r
        JOIN users u ON r.user_id = u.user_id
        JOIN tests t ON r.code = t.code
        WHERE t.author_id = $1
        ORDER BY r.code, r.percentage DESC, r.timestamp ASC
    """
    result_data = await db.execute(sql, user_id, fetch=True)

    if not result_data:
        await message.answer("🕳 Siz yaratgan testlarda hali hech kim qatnashmagan.")
        return

    # Javobni yig‘ish
    response = "📊 *Siz yaratgan testlar natijalari:*\n"
    current_code = None
    rank = 1

    for row in result_data:
        full_name = row["full_name"]
        code = row["code"]
        correct = row["correct_answer"]
        incorrect = row["incorrect_answer"]
        percentage = row["percentage"]

        if current_code != code:
            current_code = code
            rank = 1
            response += f"\n🔑 *Test kodi:* {code}\n"

        response += f"{rank}. {full_name} | {correct}/{correct + incorrect} | 📈{percentage}%\n"
        rank += 1

    await message.answer(response, parse_mode="Markdown")
