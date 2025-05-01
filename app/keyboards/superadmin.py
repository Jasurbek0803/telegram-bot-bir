from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

superadmin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Test Yaratish"),KeyboardButton(text="✍️ Test Yechish")],
        [KeyboardButton(text="🗑 Test O'chirish"),KeyboardButton(text="👀  Testlarni Ko'rish")],
        [KeyboardButton(text="Admin Qo'shish"), KeyboardButton(text="Adminni O'chirish"),KeyboardButton(text="Test Natijalari")]
    ],
    resize_keyboard=True
)


back_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Ortga")],
    ],
    resize_keyboard=True
)
