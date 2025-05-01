import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

from app.config import load_config

from app.handlers.superadmin import startAll
from app.handlers.user import  registrationUser, test_yechish, about
from app.handlers.superadmin.all import router as superadmin_router
from app.utils.database import Database
from app.utils.db_setup import sync_admins_from_config


async def main():
    db = Database()
    config = load_config()
    sync_admins_from_config()

    try:
        db.create_all_tables()
    except Exception as error:
        print(error)

    bot_token: str
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    db = Database(path_to_db="main.db")
    # Handlers ro'yxati
    dp.include_routers(
        superadmin_router,
        startAll.router,
        registrationUser.router,
        test_yechish.router,
        about.router,



    )

    # Start komandasi
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="help", description="Botni boshlash"),

    ])

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
