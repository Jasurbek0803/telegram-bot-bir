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
    # config.py

    SUPERADMINS = [
        6551039574  # o'zingizning user_id
        # yana biri bo'lsa
    ]

    ADMINS = [
         # admin1
         # admin2
    ]


def load_config():
    return Config()
