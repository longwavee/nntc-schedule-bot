from settings import bot, dp
from handlers import messages, callbacks
from schedule.parser.updater import schedule_updater
import asyncio
import logging

logging.basicConfig(level=logging.INFO,
                    filename='logs/bot_logs.log',
                    format='%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]',
                    datefmt='%d.%m.%Y %I:%M:%S',
                    encoding = 'utf-8',
                    filemode='w')

async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(messages.router)
    dp.include_router(callbacks.router)

    await asyncio.gather(
        dp.start_polling(bot),
        schedule_updater(True)
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"Bot terminated due to an error: {e}")
    except KeyboardInterrupt:
        pass


