import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu, back_button
from app.states.test_yechish import SolveTestStates
from app.utils.database import Database

import re

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


def normalize_user_answers(raw: str) -> str:
    raw = raw.upper().strip()
    answers = re.findall(r"[A-E]", raw)
    return "".join(answers)

def calculate_result(user_answers: str, correct_answers: str):
    correct_answers = correct_answers.upper()
    correct = sum(u == c for u, c in zip(user_answers, correct_answers))
    total = len(correct_answers)
    wrong = total - correct
    percentage = round((correct / total) * 100, 2)
    return correct, wrong, percentage



@router.message(F.text == "✍️ Test Yechish")
async def test_start(message: Message, state: FSMContext):

    await message.answer("Iltimos, testning maxsus kodini kiriting:",reply_markup=back_button)
    await state.set_state(SolveTestStates.waiting_for_test_code)

@router.message(SolveTestStates.waiting_for_test_code)
async def receive_code(message: Message, state: FSMContext):
    code_text = message.text.strip()

    if not code_text.isdigit():
        await message.answer("Kod faqat raqamlardan iborat bo'lishi kerak.")
        return

    code = int(code_text)
    test = db.get_test_by_code(code)  # (code, answers, center, owner)

    if not test:
        await message.answer("Bunday maxsus kodli test topilmadi.")
        await state.clear()
        return

    if db.has_user_taken_test(message.from_user.id, code):
        await message.answer("Siz bu testni allaqachon yechgansiz.")
        await state.clear()
        return

    # Faqat test_id (code) va correct_answers ni saqlaymiz
    await state.update_data(code=test[0], correct_answers=test[1])
    await message.answer("Test topildi ✅\nEndi javoblaringizni kiriting (masalan: abcdabcd yoki 1a2b3c4d...)")
    await state.set_state(SolveTestStates.waiting_for_answers)

@router.message(SolveTestStates.waiting_for_answers)
async def receive_answers(message: Message, state: FSMContext):
    data = await state.get_data()
    correct_answers = data["correct_answers"]
    code = data["code"]

    user_answers = normalize_user_answers(message.text)

    if len(user_answers) != len(correct_answers):
        await message.answer(f"Javoblar soni noto‘g‘ri. To‘g‘ri javoblar soni: {len(correct_answers)} ta. Qaytadan kiriting:")
        return
    calculate_result(user_answers, correct_answers)
    correct, wrong, percent = calculate_result(user_answers, correct_answers)

    full_name = f"{message.from_user.last_name or ''} {message.from_user.first_name or ''}".strip()

    db.save_result(
        full_name=full_name,
        user_id=message.from_user.id,
        code=code,
        correct=correct,
        incorrect=wrong,
        percentage=percent
    )

    await message.answer(
        f"✅ Test natijasi:\n"
        f"Jami savollar: {len(correct_answers)}\n"
        f"To‘g‘ri javoblar: {correct}\n"
        f"Noto‘g‘ri javoblar: {wrong}\n"
        f"Foiz: {percent}%\n"
        f"📌 Natijangiz bazaga saqlandi."
    )
    await state.clear()
