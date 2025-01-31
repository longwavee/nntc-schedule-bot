from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from settings import URL_SCHEDULE
import os

def menu_Kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🗓 Расписание"),
           KeyboardButton(text="👀 Мое расписание"))
    kb.row(KeyboardButton(text="🕘 График прихода"),
           KeyboardButton(text="📁 Сайт", web_app=WebAppInfo(url=URL_SCHEDULE)))
    return kb.as_markup(resize_keyboard=True)