import datetime
import typing

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from sqlalchemy import delete

from core.create_connect import session_factory
from db.models import User, Group, GroupUser


async def insert_user(user: User):
    async with session_factory() as session:
        async with session.begin():
            query = insert(User).values(
                telegram_id=user.telegram_id,
                fullname=user.fullname,
                shortname=user.shortname,
                photo=user.photo,
                telegram_name=user.telegram_name,
                telegram_username=user.telegram_username
            )
            query = query.on_conflict_do_update(
                index_elements=['telegram_id'],
                set_=dict(fullname=user.fullname,
                          shortname=user.shortname,
                          photo=user.photo,
                          telegram_name=user.telegram_name,
                          telegram_username=user.telegram_username,
                          updated_at=datetime.datetime.now())
            )
            await session.execute(query)
            await session.commit()
            await session.close()


async def insert_group(group: Group):
    async with session_factory() as session:
        async with session.begin():
            query = insert(Group).values(
                title=group.title,
                description=group.description
            )
            query = query.on_conflict_do_update(
                index_elements=['title'],
                set_=dict(description=group.description,
                          updated_at=datetime.datetime.now())
            )
            await session.execute(query)
            await session.commit()
            await session.close()


async def select_all_groups():
    list_groups = []
    async with session_factory() as session:
        async with session.begin():
            query = select(Group)
            groups = await session.execute(query)
            for group in groups.scalars():
                list_groups.append(group.title)
    return list_groups


async def select_user(telegram_id):
    async with session_factory() as session:
        async with session.begin():
            user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalars().one()
            return user


async def select_groups_for_user(telegram_id):
    list_groups = []
    async with session_factory() as session:
        async with session.begin():
            query = select(Group).join(GroupUser).join(User).where(User.telegram_id == telegram_id)
            groups = await session.execute(query)
            for group in groups.scalars():
                list_groups.append(group.title)
    return list_groups


async def insert_groups_user(telegram_id: int, groups: typing.List[str]):
    async with session_factory() as session:
        async with session.begin():
            user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalars().one()
            delete_stmt = delete(GroupUser).where(GroupUser.user_id == user.id)
            await session.execute(delete_stmt)
            for group_title in groups:
                group = (await session.execute(select(Group).where(Group.title == group_title))).scalars().one()
                stmt = insert(GroupUser).values(user_id=user.id, group_id=group.id)
                await session.execute(stmt)
            await session.commit()
            await session.close()
