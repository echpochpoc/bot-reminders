import datetime
import typing

from sqlalchemy.dialects.postgresql import insert
# from sqlalchemy.future import select
from sqlalchemy import delete, join, select

from core.create_connect import session_factory
from db.models import User, Group, GroupUser, Reminder, ReminderUser


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
                list_groups.append(group)
    return list_groups


async def select_user(telegram_id):
    async with session_factory() as session:
        async with session.begin():
            user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalars().one()
            return user


async def select_user_all():
    async with session_factory() as session:
        async with session.begin():
            user = (await session.execute(select(User))).scalars()
            return user


async def select_reminder_for_me(telegram_id: int) -> list[Reminder]:
    reminders_list = []
    async with session_factory() as session:
        async with session.begin():
            query = select(Reminder).join(
                ReminderUser, Reminder.id == ReminderUser.reminder_id) \
                .join(User, User.id == ReminderUser.user_id) \
                .where(User.telegram_id == telegram_id, ReminderUser.done == False)
            reminders = await session.execute(query)
            for reminder in reminders.scalars():
                reminders_list.append(reminder)
    return reminders_list


async def select_my_reminders(telegram_id: int) -> list[Reminder]:
    async with session_factory.begin() as session:
        stmt = select(Reminder).join(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        reminder = result.scalars().all()
        return reminder


async def select_groups_for_user(telegram_id: int):
    list_groups = []
    async with session_factory() as session:
        async with session.begin():
            query = select(Group).join(GroupUser).join(User).where(User.telegram_id == telegram_id)
            groups = await session.execute(query)
            for group in groups.scalars():
                list_groups.append(group.title)
    return list_groups


async def select_groups_users(groups_id: list):
    list_users = []
    async with session_factory() as session:
        async with session.begin():
            user = (await session.execute(select(User).join(GroupUser).where(
                GroupUser.group_id.in_(groups_id)).distinct())).scalars()
    for i in user:
        list_users.append(i)
    return list_users


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


async def insert_reminder(reminder: Reminder, users: list[int]):
    async with session_factory() as session:
        async with session.begin():
            query = insert(Reminder).values(
                creator_id=reminder.creator_id,
                text=reminder.text,
                date_delete=reminder.date_delete,
                times=reminder.times,
                dates=reminder.dates,
                days_week=reminder.days_week,
            ).returning(Reminder.id)
            rem = await session.execute(query)
            for i in rem.scalars():
                rem_id = i
            for user in users:
                reminders_users = ReminderUser(
                    user_id=user,
                    reminder_id=rem_id,
                )
                session.add(reminders_users)
            await session.commit()


async def update_reminder_done(rem_id: int, user_id: int):
    async with session_factory.begin() as session:
        stmt = select(ReminderUser).where(ReminderUser.reminder_id == rem_id,
                                          ReminderUser.user_id == user_id)
        result = await session.execute(stmt)
        reminder_user: ReminderUser = result.scalar_one()
        reminder_user.done = True


async def select_user_reminder_done(rem_id: int) -> list[ReminderUser.user_id, ReminderUser.done]:
    async with session_factory.begin() as session:
        stmt = select(User.shortname, ReminderUser.done).where(ReminderUser.reminder_id == rem_id)
        result = await session.execute(stmt)
        users = result.all()
        return users


async def delete_reminder(reminder_id: int):
    async with session_factory.begin() as session:
        reminder = await session.get(Reminder, reminder_id)
        await session.delete(reminder)


async def test():
    async with session_factory.begin() as session:
        stmt = select(ReminderUser.reminder_id)
        result = await session.execute(stmt)
        reminder_user = result.scalar_one()
        for r in reminder_user:
            print(r)
