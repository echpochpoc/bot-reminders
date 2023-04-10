from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core import BOT_TOKEN, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME

storage = MemoryStorage()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


engine = create_async_engine(f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}'
                             f'@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}')


session_factory = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
