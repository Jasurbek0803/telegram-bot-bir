from aiogram import Router, F
from aiogram.types import Message

from app.utils.database import Database  # YANGI: database.py dan foydalanamiz

router = Router()
db = Database()



@router.message(F.text == "👀  Testlarni Ko'rish")
async def view_all_tests_grouped_by_owner(message: Message):
    user_id = message.from_user.id

    if not db.is_admin(user_id) and not db.is_superadmin(user_id):
        await message.answer("❌ Siz admin emassiz!\nAdmin bo'lish uchun ushbu raqamga bog'laning: +998932244730")
        return

    if db.is_superadmin(user_id):
        sql = "SELECT code, answers, center_name, author FROM tests"
        tests = db.execute(sql, fetchall=True)
    else:
        sql = "SELECT code, answers, center_name, author FROM tests WHERE author_id = ?"
        tests = db.execute(sql, (user_id,), fetchall=True)

    if not tests:
        await message.answer("📭 Hech qanday test mavjud emas.")
        return

    grouped_tests = {}
    for code, answers, center_name, author in tests:
        unique_owner = f"{center_name} - {author}"
        if unique_owner not in grouped_tests:
            grouped_tests[unique_owner] = []
        grouped_tests[unique_owner].append(
            f"🆔 Maxsus kod: {code}\n"
            f"✅ Javoblar: {answers}"
        )

    for owner_key, testlar in grouped_tests.items():
        text = f"👤 {owner_key} ga tegishli testlar:\n\n"
        for i, test in enumerate(testlar, start=1):
            text += f"📄 Test #{i}\n{test}\n\n"
        await message.answer(text.strip())
