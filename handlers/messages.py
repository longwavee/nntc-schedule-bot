from settings import c, db, bot, ADMINS_ID
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from keyboards import reply, inline
import os
import logging
from datetime import datetime

router = Router()


@router.message(Command("start"))
async def start_message_handler(message: Message):
    user = message.from_user
    current_datetime = datetime.now().strftime('%d.%m.%Y %I:%M:%S')
    c.execute("INSERT OR IGNORE INTO users"
              "(id, first_name, last_name, username, selected_group, join_datetime)"
              "VALUES (?, ?, ?, ?, ?, ?)",
              (user.id, user.first_name, user.last_name, user.username, None, current_datetime))
    db.commit()
    await message.answer(text="<b>Бот расписания НРТК <u>(БЕТА)</u></b>\n\n"
                              "💎 Мгновенный доступ к информации с сайта расписания <b>для вашего удобства</b>.\n\n"
                              "❕ Проверяйте актуальность самостоятельно в случае сомнений.",
                         reply_markup=reply.menu_Kb(),
                         parse_mode="HTML",
                         disable_notification=True)


@router.message(F.text == "🗓 Расписание")
async def schedule_message_handler(message: Message):
    await message.answer(text="<b>Выберите курс:</b>",
                         reply_markup=inline.courses_Kb(),
                         parse_mode="HTML",
                         disable_notification=True)


@router.message(F.text == "👀 Мое расписание")
async def my_schedule_message_handler(message: Message):
    c.execute("SELECT selected_group FROM users WHERE id = ?", (message.from_user.id,))
    my_group = c.fetchone()
    message_text = '📕 <b>Нет добавленной группы.</b>\n\nЧто бы добавить группу в избранное, напишите команду <code>/profile</code> и нажмите на кнопку "Моя группа".'
    markup = None
    if my_group is not None and my_group[0]:
        c.execute("SELECT id FROM groups WHERE name = ?", (my_group[0],))
        group = c.fetchone()
        if group:
            message_text = "<b>Выберите день:</b>"
            markup = inline.days_Kb(group[0], my_group[0][0])
        else:
            message_text = "🚫 <b>Ошибка</b>\nЗаданная вами группа не найдена в расписании, попробуйте ее изменить."
    await message.answer(text=message_text,
                         reply_markup=markup,
                         parse_mode="HTML",
                         disable_notification=True)


@router.message(F.text == "🕘 График прихода")
async def arrival_schedule_message_handler(message: Message):
    await message.answer_photo(photo=FSInputFile("schedule/arrival_schedule.png"),
                               disable_notification=True)


@router.message(Command("profile"))
async def profile_message_handler(message: Message):
    user = message.from_user
    c.execute("SELECT * FROM users WHERE id = ?", (user.id,))
    user_db = c.fetchone()
    message_text = "🚫 <b>Ошибка</b>\nПерезагрузите бота и попробуйте снова."
    markup = None
    if user_db and isinstance(user_db, tuple):
        message_text = ("👤 <b>Профиль</b>\n\n"
                        f"<b>ID:</b>   <code>#{user.id}</code>\n"
                        f"<b>Имя:</b>  {user.first_name if user.first_name else user.username}\n"
                        f"<b>Группа:</b>  {user_db[4] if user_db[4] else 'Не добавлена.'}")
        markup = inline.profile_Kb()
    await message.answer(text=message_text,
                         reply_markup=markup,
                         parse_mode="HTML",
                         disable_notification=True)


@router.message(Command("teachers"))
async def teacher_message_handler(message: Message):
    await message.answer(text="<b>Выбери день:</b>",
                         parse_mode="HTML",
                         reply_markup=inline.days_teacher_Kb(),
                         disable_notification=True)


async def update_schedule_notification(detector):
    c.execute("SELECT id FROM users")
    users = c.fetchall()
    if users and isinstance(users, list) and detector:
        for user in users:
            try:
                await bot.send_message(chat_id=user[0],
                                       text="📝 <b>Обнаружено изменение в расписании!</b>",
                                       parse_mode="HTML")
            except Exception as e:
                logging.warning(f"The schedule change message was not sent to the user '{user[0]}' due to an error:\n{e}")


@router.message(F.text.startswith("/notification:"))
async def notification_message_handler(message: Message):
    if not message.from_user.id in ADMINS_ID:
        return
    text_query = message.text.split(':')
    if text_query[1]:
        message_text = f"🔔 <b>Уведомление:</b>{text_query[1]}"
        c.execute("SELECT id FROM users")
        users = c.fetchall()
        if users and isinstance(users, list):
            for user in users:
                try:
                    await bot.send_message(chat_id=user[0],
                                        text=message_text,
                                        parse_mode="HTML")
                except Exception as e:
                    logging.warning(f"The notification was not sent to the user '{user[0]}' due to an error:\n{e}")


@router.message(F.caption == ("/update_arrival"))
async def update_arrival_message_handler(message: Message):
    if not message.from_user.id in ADMINS_ID:
        return
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    photo_save_path = os.path.join("./schedule/", f"arrival_schedule.png")
    await bot.download_file(file.file_path, photo_save_path)

    await message.answer(text=f"✅ <b>Фото графика прихода успешно сохранено!</b>",
                        parse_mode="HTML")

@router.message(Command("bot_data"))
async def get_count_users_message_handler(message: Message):
    if not message.from_user.id in ADMINS_ID:
        return
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()
    await message.answer(text=f"👤 Пользователей в боте: <b>{users[0]}</b>",
                        parse_mode="HTML")

@router.message(Command("get_db"))
async def get_database_message_handler(message: Message):
    if not message.from_user.id in ADMINS_ID:
        return
    await message.answer_document(document=FSInputFile("d_base.db"))
        