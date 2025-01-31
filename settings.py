from aiogram import Bot, Dispatcher
import sqlite3
import os


BOT_TOKEN = os.environ.get("BOT_TOKEN")
URL_SCHEDULE = os.environ.get("URL_SCHEDULE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ADMINS_ID = (6643395551,)

db = sqlite3.connect("d_base.db", check_same_thread=False)
c = db.cursor()
