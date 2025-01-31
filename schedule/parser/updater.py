from settings import URL_SCHEDULE
from bs4 import BeautifulSoup
from schedule.parser.pulling import pulling_in_pdf
import asyncio
import aiohttp
import aiofiles
import os
import logging
from datetime import datetime
import pytz

async def request_on_download(pin_notification):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(URL_SCHEDULE) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            app_content = soup.select_one('div#app-content')
            link_download_pdf = app_content.select_one('input#downloadURL')['value']
            async with session.get(link_download_pdf) as response_pdf:
                pdf_content = await response_pdf.read()
                async with aiofiles.open("schedule/schedule.pdf", 'wb') as file:
                    await file.write(pdf_content)
                return await pulling_in_pdf(pin_notification)

async def fetch_size_log(size_log):
    async with aiofiles.open(size_log, 'r') as file:
        return await file.readline()

async def update_size_log(size_log, weight):
    async with aiofiles.open(size_log, 'w') as file:
        await file.write(weight)


async def schedule_updater(while_updates):
    size_log = "logs/size_schedule.log"
    p_weight = None
    pin_notification = True
    moscow_timezone = pytz.timezone('Europe/Moscow')
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        while while_updates:
            try:
                async with session.get(URL_SCHEDULE) as response:
                    if response.status == 200:
                        soup = BeautifulSoup(await response.text(), 'html.parser')
                        weight = soup.select_one('input#filesize')['value']
                        if os.path.exists(size_log):
                            p_weight = await fetch_size_log(size_log)
                        if datetime.now(moscow_timezone).strftime("%H:%M") in ["15:00", "18:00", "6:00"] and pin_notification is False:
                            pin_notification = True
                        if weight != p_weight:
                            await update_size_log(size_log, weight)
                            await request_on_download(pin_notification)
                            pin_notification = False
            except Exception as e:
                logging.error(f"Schedule update error: {e}")
                pass
            await asyncio.sleep(60)
