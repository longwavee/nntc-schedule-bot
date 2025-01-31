from settings import c
import json
import re
from schedule.handlers.schedule import lesson_handler


def selection_all_teacher(query_day):
    teachers = set()
    c.execute("SELECT elements FROM schedule WHERE id_day = ?", (query_day,))
    json_schedules = c.fetchall()
    if json_schedules:
        for json_element_schedules in json_schedules:
            convert_schedule = json.loads(json_element_schedules[0])
            for element_schedule in convert_schedule:
                teachers.update(re.sub(r',', '.', name) for name in
                                re.findall(r'[А-Яа-я]+\s[А-Я][.,][А-Я][.,]', element_schedule[1] or ''))
    else:
        return

    sorted_teachers = sorted(teachers)
    n = len(sorted_teachers) // 3
    return sorted_teachers[:n], sorted_teachers[n:2 * n], sorted_teachers[2 * n:]


async def selection_lessons_teacher(day, query_teacher):
    lessons = []
    c.execute("SELECT name FROM days WHERE id = ?", (day,))
    format_day = c.fetchone()
    c.execute("SELECT id_group, elements FROM schedule WHERE id_day = ?", (day,))
    json_schedules = c.fetchall()
    if json_schedules:
        for id_group, json_element_schedules in json_schedules:
            convert_schedule = json.loads(json_element_schedules)
            seen_lesson = None
            for element_schedule in convert_schedule:
                if element_schedule[2] is not None:
                    seen_lesson = element_schedule
                teacher_names = (re.sub(r',', '.', name) for name in
                                 re.findall(r'[А-Яа-я]+\s[А-Я][.,][А-Я][.,]', element_schedule[1] or ''))
                if query_teacher in teacher_names:
                    for i in range(2, 5):
                        if not element_schedule[i] and seen_lesson:
                            element_schedule[i] = seen_lesson[i]
                    c.execute("SELECT name FROM groups WHERE id = ?", (id_group,))
                    element_schedule[1] = c.fetchone()[0]
                    lessons.append(element_schedule)

    def get_sort_key(lesson):
        if lesson[3] is None:
            return 1
        match = re.match(r'(\d+)-(\d+)\s(.*)', lesson[3])
        if isinstance(lesson[3], str) and lesson[3].isdigit():
            return int(lesson[3])
        elif match:
            return int(match.group(1))
        else:
            return -1
    sorted_lessons = sorted(lessons, key=get_sort_key)

    result = await lesson_handler(format_day[0], sorted_lessons)
    return result