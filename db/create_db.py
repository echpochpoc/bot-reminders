import asyncio
import asyncpg

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import *
from db.models.base import Base


async def connect_to_db(database, password, user):
    try:
        await asyncpg.connect(user=user, database=database, password=password)
        print('Database connect')
    except asyncpg.exceptions.ConnectionDoesNotExistError:
        sys_conn = await asyncpg.connect(user=user, password=password)
        await sys_conn.execute(f'CREATE DATABASE "{database}" OWNER "{user}"')
        await sys_conn.close()
        print('Database created')


async def create_models():
    engine = create_async_engine(f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}'
                                 f'@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print('Models drop and create')


asyncio.run(connect_to_db(user=DATABASE_USER, database=DATABASE_NAME, password=DATABASE_PASSWORD))
asyncio.run(create_models())
