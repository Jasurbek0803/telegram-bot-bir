import os
from dataclasses import dataclass

from aiogram import Dispatcher
from aiogram.fsm import storage
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        self.superadmin_token = os.getenv("SUPER_ADMIN_ID")

    # config.py
    SUPERADMINS = [
        6551039574  # o'zingizning user_id
        # yana biri bo'lsa
    ]

    ADMINS = [
         # admin1
         # admin2
    ]
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")


def load_config():
    return Config()
