from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

registrationUser = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Registratsiya")],
    ],
    resize_keyboard=True
)
contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

user_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✍️ Test Yechish"), KeyboardButton(text="➕ Test Yaratish")],
        [KeyboardButton(text="🎁 Sertifikat"),KeyboardButton(text="⚙️ Sozlamalar")],
        [KeyboardButton(text="ℹ️ Biz haqimizda")]
    ],
    resize_keyboard=True
)
settings_in  = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Shaxsiy ma'lumotlarni o'zgartirish 🔄")],
        [KeyboardButton(text="🔙 Ortga")]
    ],
    resize_keyboard=True
)




back_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Ortga")],
    ],
    resize_keyboard=True
)

