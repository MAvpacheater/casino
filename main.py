import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import os
from dotenv import load_dotenv
from handlers import register_handlers

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 100,
            ref_by INTEGER,
            last_daily_bonus INTEGER,
            last_hourly_bonus INTEGER
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
