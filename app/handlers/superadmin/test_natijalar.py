from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu
from app.states.admin import AdminStates
from app.utils.database import Database


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

@router.message(F.text == "Test Natijalari")
async def test_yechganlar(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Faqat admin yoki superadmin bo‘lishi shart
    if not (db.is_admin(user_id) or db.is_superadmin(user_id)):
        await message.answer("Sizda bu bo'limga ruxsat yo'q.")
        return

    # Yangi funksiyadan foydalanamiz
    result_data = db.get_test_results_by_author_id(user_id)

    if not result_data:
        await message.answer("Siz yaratgan testlarda hali hech kim qatnashmagan.")
        return

    # Testlar bo‘yicha reyting chiqarish
    response = "📊 *Siz yaratgan testlar natijalari:*\n\n"
    current_code = None
    rank = 1

    for row in result_data:
        full_name, code, correct, incorrect, percentage = row

        if current_code != code:
            current_code = code
            rank = 1
            response += f"\n🔑 *Test kodi:* {code}\n"

        response += (f"{rank}.{full_name} | {correct}/{correct+incorrect} | 📈{percentage}%\n")
        rank += 1

    await message.answer(response, parse_mode="Markdown")
