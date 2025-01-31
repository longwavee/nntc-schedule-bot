import pdfplumber
from settings import db, c
import json
from handlers.messages import update_schedule_notification
import logging

async def pulling_in_pdf(pin_notification):
    json_data = {}
    weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
    group = "Неизвестно"
    day = "Неизвестно"

    with pdfplumber.open("schedule/schedule.pdf") as pdf:
        for page in pdf.pages[:-1]:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split('\n')[:10]:
                if line.startswith(tuple(weekdays)):
                    day = line

            tables_on_page = page.extract_tables()
            if not tables_on_page:
                continue
            for table in tables_on_page:
                for row in table:
                    if len(row) < 6:
                        row.insert(2, None)
                    if row[1] is not None and row[1].startswith(tuple(weekdays)):
                        continue
                    if row[0] == "" and row[1] == "Преподаватель" and row[2] == "Дисциплина, МДК":
                        continue
                    if all(i == '' for i in row):
                        json_data.setdefault(group, {}).setdefault(day, []).append(row)
                        continue

                    if row[1] == "":
                        row[1] = "нет"
                    if row[1] is not None and row[1][0].isdigit() and row[1].find('-') != -1:
                        group = row[1]
                        continue

                    json_data.setdefault(group, {}).setdefault(day, []).append(row)
    return await filling_database(json_data, pin_notification)


async def filling_database(json_data, pin_notification):
    c.execute("DELETE FROM schedule")
    c.execute("DELETE FROM groups")
    c.execute("DELETE FROM days")

    group_id = schedule_id = days_id = 1
    seen_group = set()
    seen_day = {}

    for group, elements_schedule in json_data.items():
        if group not in seen_group:
            seen_group.add(group)
            c.execute("INSERT OR IGNORE INTO groups (id, name) VALUES (?, ?)", (group_id, group))
            group_id += 1
        for day, schedule in elements_schedule.items():
            if day not in seen_day:
                c.execute("INSERT OR IGNORE INTO days (id, name) VALUES (?, ?)", (days_id, day))
                seen_day[day] = days_id
                days_id += 1
            day_id = seen_day[day]
            c.execute("INSERT OR IGNORE INTO schedule (id, id_group, id_day, elements) VALUES (?, ?, ?, ?)",
                      (schedule_id, group_id - 1, day_id, json.dumps(schedule)))
            schedule_id += 1

    db.commit()
    logging.info("Schedule changed.")
    await update_schedule_notification(pin_notification)
