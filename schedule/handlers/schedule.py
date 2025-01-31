import asyncio
import re

existing_class_hour = False

async def lesson_handler(day, lessons):
    global existing_class_hour
    existing_class_hour = False
    result = ""
    seen_text = None
    seen = {key: None for key in ['order', 'teacher', 'discipline', 'audience', 'arrival_time']}

    for lesson in lessons:
        attributes = {
            'order': lesson[3],
            'teacher': lesson[1],
            'discipline': lesson[2],
            'audience': lesson[4],
            'arrival_time': lesson[5]
        }

        for key in attributes:
            if attributes[key] is None:
                attributes[key] = seen[key]
            else:
                seen[key] = attributes[key]

        element_handlers = await asyncio.gather(
            order_handler(day, attributes["order"]),
            discipline_handler(attributes["discipline"]),
            teacher_handler(attributes["teacher"]),
            audience_handler(attributes["audience"]),
            arrival_time_handler(attributes["arrival_time"])
        )

        if all(i == '' for i in element_handlers):
            element_txt = "Нет пар"
        else:
            element_txt = ''.join(element_handlers)
        result += f"{element_txt}\n" if element_txt != seen_text else ''
        seen_text = element_txt
    return result


async def order_handler(day, order):
    global existing_class_hour
    if order == '' and (day.startswith("понедельник") or day.startswith("четверг")):
        if existing_class_hour is False:
            existing_class_hour = True
            return "<b>Классный час</b>\n"
    if order is None or order == '':
        return ''
    return f"<b>{order}.</b> "


async def teacher_handler(teacher):
    if teacher is None or teacher == '':
        return ''
    if re.match(r'^[А-Яа-я]+\s[А-Я]\.[А-Я]\.$', teacher) \
    or re.match(r'^[А-Яа-я]+\s[А-Я]\.[А-Я]\./[А-Яа-я]+\s[А-Я]\.[А-Я]\.$', teacher):
        return f"Преподаватель: {teacher}\n"
    if teacher == "нет":
        return "<b>Нет</b>\n"
    if teacher[0].isdigit() and teacher.find('-') != -1:
        return f"Группа: {teacher}\n"
    return f"<b>{teacher}</b>\n"


async def discipline_handler(discipline):
    if discipline is None or discipline == '':
        return ''
    return f"<b>{discipline.strip().capitalize()}</b>\n"


async def audience_handler(audience):
    if audience is None or audience == '':
        return ''
    return f"Аудитория: <u>{audience}</u>\n"


async def arrival_time_handler(arrival_time):
    if arrival_time is None or arrival_time == '':
        return ''
    return f"Время прихода: {arrival_time}\n"