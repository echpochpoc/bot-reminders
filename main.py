import logging
import os

from aiogram.utils import executor

from core import bot, dp
from core.handlers import basic
from core.utils import commands


async def on_startup(_):
    await bot.set_webhook(os.getenv('URL_DOMAIN'))
    await commands.set_commands(bot)
    await bot.send_message(chat_id=os.getenv('ADMIN_ID'), text='Bot start')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - [%(levelname)s] - %(name)s - '
                               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')


async def on_shutdown(_):
    await bot.delete_webhook()
    await bot.send_message(chat_id=os.getenv('ADMIN_ID'), text='Bot stop')


basic.register_handler_basic(dp)


executor.start_webhook(
    dispatcher=dp,
    webhook_path=os.getenv('URL_PATH'),
    on_startup=on_startup,
    on_shutdown=on_shutdown,
    skip_updates=True,
    host=os.getenv('SERVER_HOST'),
    port=os.getenv('SERVER_PORT')
)
