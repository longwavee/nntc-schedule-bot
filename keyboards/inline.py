from settings import c
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from schedule.handlers.teachers import selection_all_teacher


def courses_Kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    c.execute("SELECT name FROM groups")
    groups = c.fetchall()
    if groups and isinstance(groups, list):
        seen_course = set()
        for group in groups:
            if group[0][0] not in seen_course:
                seen_course.add(group[0][0])
                kb.button(text=group[0][0], callback_data=f"groups:{group[0][0]}")
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.adjust(5)
    return kb.as_markup(resize_keyboard=True)


def groups_Kb(query_course) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    c.execute("SELECT id, name FROM groups")
    groups = c.fetchall()
    if groups and isinstance(groups, list):
        for id_group, group in groups:
            if group[0][0] == query_course:
                kb.button(text=group, callback_data=f"days:{id_group}:{group[0][0]}")
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.button(text="Назад", callback_data="courses")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def days_Kb(query_group, query_course) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    c.execute("SELECT id_day FROM schedule WHERE id_group = ?", (query_group,))
    id_days = c.fetchall()
    if id_days and isinstance(id_days, list):
        for id_day in id_days:
            c.execute("SELECT name FROM days WHERE id = ?", (id_day[0],))
            day = c.fetchone()
            if day:
                kb.button(text=day[0], callback_data=f"schedule:{query_group}:{id_day[0]}")
            else:
                kb.button(text="🚫 Ошибка", callback_data="error")
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.button(text="Назад", callback_data=f"groups:{query_course}")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def schedule_Kb(query_group) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    c.execute("SELECT name FROM groups WHERE id = ?", (query_group,))
    name_group = c.fetchone()
    if name_group:
        kb.button(text="Назад", callback_data=f"days:{query_group}:{name_group[0][0]}")
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def profile_Kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Моя группа", callback_data="my_group")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def courses_my_group_Kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    c.execute("SELECT name FROM groups")
    groups = c.fetchall()
    if groups and isinstance(groups, list):
        seen_course = set()
        for group in groups:
            if group[0][0] not in seen_course:
                seen_course.add(group[0][0])
                kb.button(text=group[0][0], callback_data=f"choice_my_group:{group[0][0]}")
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.adjust(5)
    return kb.as_markup(resize_keyboard=True)


def add_my_group_Kb(query_course) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    c.execute("SELECT id, name FROM groups")
    groups = c.fetchall()
    if groups and isinstance(groups, list):
        for id, group in groups:
            if group[0] == query_course:
                kb.button(text=group, callback_data=f"add_my_group:{id}")
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.button(text="Назад", callback_data="my_group")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def days_teacher_Kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    c.execute("SELECT id, name FROM days")
    days = c.fetchall()
    if days and isinstance(days, list):
        seen_elements = set()
        for id_day, name in days:
            if name not in seen_elements:
                seen_elements.add(name)
                kb.button(text=name, callback_data=f"teachers:{id_day}")
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def teachers_Kb(query_day, page) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    teachers_list = selection_all_teacher(query_day)
    if teachers_list:
        current_list = teachers_list[page - 1]
        for teacher in current_list:
            kb.button(text=teacher, callback_data=f"sch_teacher:{query_day}:{teacher}")
        kb.adjust(1)
        if page == 1:
            kb.row(InlineKeyboardButton(text="✖️", callback_data="none"),
                   InlineKeyboardButton(text=f"стр.{page + 1} ▶️", callback_data=f"n_techs:{query_day}:{page}"))
        elif page == 3:
            kb.row(InlineKeyboardButton(text=f"◀️ стр.{page - 1}", callback_data=f"p_techs:{query_day}:{page}"),
                   InlineKeyboardButton(text="✖️", callback_data="none"))
        else:
            kb.row(InlineKeyboardButton(text=f"◀️ стр.{page - 1}", callback_data=f"p_techs:{query_day}:{page}"),
                   InlineKeyboardButton(text=f"стр.{page + 1} ▶️", callback_data=f"n_techs:{query_day}:{page}"))
    else:
        kb.button(text="🚫 Ошибка", callback_data="error")
    kb.row(InlineKeyboardButton(text="Назад", callback_data="days_teachers"))
    return kb.as_markup(resize_keyboard=True)


def schedule_teachers_Kb(query_day) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Назад", callback_data=f"teachers:{query_day}"))
    return kb.as_markup(resize_keyboard=True)