from aiogram import Router, F
from aiogram.types import Message
from utils.db import db # Sizning klassingiz

router = Router()


@router.message(F.text == "👀  Testlarni Ko'rish")
async def view_all_tests_grouped_by_owner(message: Message):
    user_id = message.from_user.id

    # Ruxsatni tekshirish
    is_admin = await db.is_admin(user_id)
    is_superadmin = await db.is_superadmin(user_id)

    if not (is_admin or is_superadmin):
        await message.answer("❌ Siz admin emassiz!\n"
                             "Admin bo'lish uchun ushbu raqamga bog'laning: +998932244730")
        return

    # SQL so‘rov va ma’lumotlarni olish
    if is_superadmin:
        sql = "SELECT code, answers, center_name, author FROM tests"
        tests = await db.execute(sql, fetch=True)
    else:
        sql = "SELECT code, answers, center_name, author FROM tests WHERE author_id = $1"
        tests = await db.execute(sql, user_id, fetch=True)

    # Hech qanday test bo'lmasa
    if not tests:
        await message.answer("📭 Hech qanday test mavjud emas.")
        return

    # Testlarni guruhlash
    grouped_tests = {}
    for row in tests:
        key = f"{row['center_name']} - {row['author']}"
        grouped_tests.setdefault(key, []).append(
            f"🆔 Maxsus kod: {row['code']}\n✅ Javoblar: {row['answers']}"
        )

    # Har bir guruh uchun alohida xabar yuborish
    for owner, test_list in grouped_tests.items():
        text = f"👤 {owner} ga tegishli testlar:\n\n"
        text += "\n\n".join([f"📄 Test #{i + 1}\n{t}" for i, t in enumerate(test_list)])
        await message.answer(text.strip())
