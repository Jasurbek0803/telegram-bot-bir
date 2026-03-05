import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin import admin_menu
from app.keyboards.superadmin import superadmin_menu
from app.keyboards.user import user_main_menu, back_button
from app.states.test_yechish import SolveTestStates

from app.utils.db import db  # PostgreSQL uchun Database klassi

router = Router()



@router.message(F.text == "🔙 Ortga")
async def back(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if await db.is_superadmin(user_id):
        await state.clear()
        await message.answer("🔑 Superadmin bosh sahifasi", reply_markup=superadmin_menu)
    elif await db.is_admin(user_id):
        await state.clear()
        await message.answer("🛠 Admin bosh sahifa", reply_markup=admin_menu)
    else:
        await state.clear()
        await message.answer("👤 Bosh sahifadasiz", reply_markup=user_main_menu)


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
    await message.answer("📥 Iltimos, testning maxsus kodini kiriting:", reply_markup=back_button)
    await state.set_state(SolveTestStates.waiting_for_test_code)


@router.message(SolveTestStates.waiting_for_test_code)
async def receive_code(message: Message, state: FSMContext):
    code_text = message.text.strip()

    if not code_text.isdigit():
        await message.answer("❗️ Kod faqat raqamlardan iborat bo'lishi kerak.")
        return

    code = int(code_text)
    test = await db.get_test_by_code(code)  # (code, correct_answers, center, owner)

    if not test:
        await message.answer("❌ Bunday maxsus kodli test topilmadi.")
        await state.clear()
        return

    if await db.has_user_taken_test(message.from_user.id, code):
        await message.answer("📌 Siz bu testni allaqachon yechgansiz.")
        await state.clear()
        return

    await state.update_data(code=test[0], correct_answers=test[1])
    await message.answer("✅ Test topildi!\n\nEndi javoblaringizni kiriting (masalan: abcdeabcde...)")
    await state.set_state(SolveTestStates.waiting_for_answers)


@router.message(SolveTestStates.waiting_for_answers)
async def receive_answers(message: Message, state: FSMContext):
    data = await state.get_data()
    correct_answers = data["correct_answers"]
    code = data["code"]

    user_answers = normalize_user_answers(message.text)

    if len(user_answers) != len(correct_answers):
        await message.answer(
            f"❗️ Javoblar soni mos emas. To‘g‘ri javoblar soni: {len(correct_answers)} ta. Qaytadan urinib ko‘ring:"
        )
        return

    correct, wrong, percent = calculate_result(user_answers, correct_answers)

    full_name = f"{message.from_user.last_name or ''} {message.from_user.first_name or ''}".strip()

    await db.save_result(
        full_name=full_name,
        user_id=message.from_user.id,
        code=code,
        correct=correct,
        incorrect=wrong,
        percentage=percent
    )

    await message.answer(
        f"📄 Sizning test natijalaringiz:\n\n"
        f"📚 Jami savollar: {len(correct_answers)} ta\n"
        f"✅ To‘g‘ri javoblar: {correct} ta\n"
        f"❌ Noto‘g‘ri javoblar: {wrong} ta\n"
        f"📊 Natija: {percent}%\n\n"
        f"✅ Natijangiz saqlandi. Omad!"
    )

    await state.clear()
