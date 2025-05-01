from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "ℹ️ Biz haqimizda")
async def about_us(message: Message):
    await message.answer("Sifatli ta\'lim Smart bilan\n\n"
                         "➡️Matematika kurslari \n"
                         "➡️Chet tillarini o'qitish (rus tili  ingliz tili)\n"
                         "➡️Mental arifmetika \n"
                         "➡️Kompyuter kurslari \n"
                         "➡️Robototexnika \n"
                         "➡️Ixtisoslashgan maktablarga tayyorlov \n\n"
                         "Mo'ljal: Bek to'yxonasi🏢 \n\n"
                         "☎️Qabulxona:⤵️\n"
                         "+998941862614 +998943293730\n")
