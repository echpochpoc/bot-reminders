from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

import os
from dotenv import load_dotenv
load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=storage)
