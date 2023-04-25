import logging

from aiogram.utils import executor

import core.filters.filters
from core import URL_DOMAIN, URL_PATH, SERVER_PORT, SERVER_HOST, ADMIN_ID
from core.create_connect import bot, dp
from core.handlers import basic, registration, last, test, admin, reminder, mailing
from core.utils import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def on_startup(_):
    await bot.delete_webhook()
    await bot.set_webhook(URL_DOMAIN)
    await commands.set_commands(bot)
    scheduler.start()
    await bot.send_message(chat_id=ADMIN_ID, text='Погнали!🌝')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - [%(levelname)s] - %(name)s - '
                               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')


async def on_shutdown(_):
    await bot.delete_webhook()
    await bot.send_message(chat_id=ADMIN_ID, text='Пррр...🌚')


scheduler = AsyncIOScheduler()
scheduler.add_job(mailing.send_reminder_scheduler, "interval", seconds=60, args=())

test.register_handler(dp)
basic.register_handler(dp)
admin.register_handler(dp)
mailing.register_handler(dp)
reminder.register_handler(dp)
registration.register_handler(dp)
last.register_handler(dp)

if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=URL_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=SERVER_HOST,
        port=SERVER_PORT
    )
    dp.filters_factory.bind(core.filters.filters.StateClassFilter)

