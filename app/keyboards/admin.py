from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

registration_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Registratsiya")],
    ],
    resize_keyboard=True
)

contact_keyboard_admin = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✍️ Test Yechish"),KeyboardButton(text="➕ Test Yaratish"),],
        [KeyboardButton(text="🗑 Test O'chirish")],
        [KeyboardButton(text="👀  Testlarni Ko'rish"),KeyboardButton(text="Test Natijalari")]
    ],
    resize_keyboard=True
)


back_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Ortga")],
    ],
    resize_keyboard=True
)
