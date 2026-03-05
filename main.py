import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import load_config
from app.handlers.superadmin import startAll
from app.handlers.user import registrationUser, test_yechish, about
from app.handlers.superadmin.all import router as superadmin_router
from app.utils.db_setup import sync_admins_from_config
from app.utils.db import db

async def main():
    # Config va DB ni chaqiramiz
    config = load_config()

    try:
        await db.create()
        await db.create_all_tables()
    except Exception as error:
        print(f"[DB Error] {error}")


    # Bot va Dispatcher
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlar qo‘shiladi
    dp.include_routers(
        superadmin_router,
        startAll.router,
        registrationUser.router,
        test_yechish.router,
        about.router
    )

    # Start komandasi
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="help", description="Yordam"),
    ])

    print("✅ Bot ishga tushdi.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
