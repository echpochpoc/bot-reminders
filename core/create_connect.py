from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models.base import Base
from core import BOT_TOKEN, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME


storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

engine = create_engine(f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}'
                       f'@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}')

Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
