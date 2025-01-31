from settings import c, db
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import inline
import json
from schedule.handlers.schedule import lesson_handler
from schedule.handlers.teachers import selection_lessons_teacher

router = Router()


@router.callback_query(F.data == "courses")
async def select_course_query_handler(query: CallbackQuery):
    await query.message.edit_text(text="<b>Выберите курс:</b>",
                                  reply_markup=inline.courses_Kb(),
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith("groups:"))
async def select_group_query_handler(query: CallbackQuery):
    button_query = query.data.split(':')
    await query.message.edit_text(text="<b>Выберите группу:</b>",
                                  reply_markup=inline.groups_Kb(button_query[1]),
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith("days:"))
async def select_day_query_handler(query: CallbackQuery):
    button_query = query.data.split(':')
    await query.message.edit_text(text="<b>Выберите день:</b>",
                                  reply_markup=inline.days_Kb(button_query[1], button_query[2]),
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith("schedule:"))
async def schedule_query_handler(query: CallbackQuery):
    query_group = query.data.split(':')[1]
    query_day = query.data.split(':')[2]
    c.execute("SELECT name FROM groups WHERE id = ?", (query_group,))
    group = c.fetchone()
    c.execute("SELECT name FROM days WHERE id = ?", (query_day,))
    day = c.fetchone()
    message_text = "🚫 <b>Ошибка</b>\nНе удалось прочитать расписание с заданными параметрами."
    markup = None
    if group and day:
        c.execute("SELECT elements FROM schedule WHERE id_group = ? AND id_day = ?", (query_group, query_day,))
        json_schedule = c.fetchone()
        if json_schedule[0]:
            data_schedule = json.loads(json_schedule[0])
            processed_schedule = await lesson_handler(day[0], data_schedule)
            message_text = f"<code>Расписание группы {group[0]}\nна '{day[0]}'</code>\n\n{processed_schedule}"
            markup = inline.schedule_Kb(query_group)
    await query.message.edit_text(text=message_text,
                                  reply_markup=markup,
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data == "my_group")
async def my_group_query_handler(query: CallbackQuery):
    await query.message.edit_text(text="<b>Выберите курс:</b>",
                                  reply_markup=inline.courses_my_group_Kb(),
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith("choice_my_group:"))
async def add_select_course_query_handler(query: CallbackQuery):
    button_query = query.data.split(':')
    await query.message.edit_text(text="<b>Выберите группу:</b>",
                                  reply_markup=inline.add_my_group_Kb(button_query[1]),
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith("add_my_group:"))
async def add_group_query_handler(query: CallbackQuery):
    button_query = query.data.split(':')
    c.execute("SELECT name FROM groups WHERE id = ?", (button_query[1],))
    name_group = c.fetchone()
    message_text = "🚫 <b>Ошибка</b>\nПерезагрузите бота и попробуйте снова."
    if name_group:
        c.execute("UPDATE users SET selected_group = ? WHERE id = ?", (name_group[0], query.from_user.id,))
        db.commit()
        message_text = "✅ <b>Группа добавленна в избранное.</b>\n\nЧтобы поменять группу, повторите процедуру."
    await query.message.edit_text(text=message_text,
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data == "days_teachers")
async def menu_teacher_query_handler(query: CallbackQuery):
    await query.message.edit_text(text="<b>Выбери день:</b>",
                                  parse_mode="HTML",
                                  reply_markup=inline.days_teacher_Kb())
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith("teachers:"))
async def teachers_query_handler(query: CallbackQuery):
    button_query = query.data.split(':')
    c.execute("SELECT name FROM days WHERE id = ?", (button_query[1],))
    day = c.fetchone()
    message_text = "🚫 <b>Ошибка</b>\nПерезагрузите бота и попробуйте снова."
    markup = None
    if day:
        message_text = f"<b>Вот все найденные преподаватели на '{day[0]}':</b>\n(стр. 1)"
        markup = inline.teachers_Kb(button_query[1], 1)
    await query.message.edit_text(text=message_text,
                                    reply_markup=markup,
                                    parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith(("p_techs:", "n_techs:")))
async def teacher_navigation_handler(query: CallbackQuery):
    action, query_day, page = query.data.split(":")
    page = int(page)
    c.execute("SELECT name FROM days WHERE id = ?", (query_day,))
    day = c.fetchone()
    message_text = "🚫 <b>Ошибка</b>\nПерезагрузите бота и попробуйте снова."
    markup = None
    if day:
        if action == "p_techs":
            page -= 1
        elif action == "n_techs":
            page += 1
        message_text = f"<b>Вот все найденные преподаватели на '{day[0]}':</b>\n(стр. {page})"
        markup = inline.teachers_Kb(query_day, page)
    await query.message.edit_text(text=message_text,
                                  reply_markup=markup,
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")


@router.callback_query(F.data.startswith("sch_teacher:"))
async def info_teacher_query_handler(query: CallbackQuery):
    button_query = query.data.split(':')
    message_text = "🚫 <b>Ошибка</b>\nПерезагрузите бота и попробуйте снова."
    markup = None
    result = await selection_lessons_teacher(button_query[1], button_query[2])
    if result:
        c.execute("SELECT name FROM days WHERE id = ?", (button_query[1],))
        day = c.fetchone()
        if day:
            message_text = f"<code>Расписание преподавателя {button_query[2]}\nна '{day[0]}'</code>\n\n{result}"
            markup = inline.schedule_teachers_Kb(button_query[1])
    await query.message.edit_text(text=message_text,
                                  reply_markup=markup,
                                  parse_mode="HTML")
    await query.answer(show_alert=True, text="")

