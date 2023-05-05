import datetime as dt

import sqlalchemy
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, select, or_

from core.create_connect import session_factory
from db.models import User, Group, GroupUser, Reminder, ReminderUser


async def insert_user(user: User) -> None:
    """
    Добавляет новых пользователей, если пользователь уже есть в базе данных обновляет данные о нем
    """
    async with session_factory.begin() as session:
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
                      telegram_username=user.telegram_username)
        )
        await session.execute(query)


async def insert_group(group: Group) -> None:
    """
    Добавляет группу
    """
    async with session_factory.begin() as session:
        query = insert(Group).values(
            title=group.title,
            description=group.description
        )
        query = query.on_conflict_do_update(
            index_elements=['title'],
            set_=dict(description=group.description,)
        )
        await session.execute(query)
        await session.commit()


async def select_groups_all() -> list[Group]:
    """
    Возвращает список объектов всех групп
    """
    async with session_factory.begin() as session:
        stmt = select(Group)
        result = await session.execute(stmt)
        groups = result.scalars().all()
        return groups


async def select_user(telegram_id: int) -> User:
    """
    Возвращает объект пользователя, по telegram id
    """
    async with session_factory.begin() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        try:
            user = result.scalar_one()
            return user
        except sqlalchemy.exc.NoResultFound:
            return None


async def select_reminder(reminder_id: int) -> Reminder:
    """
    Возвращает напоминание по id
    """
    async with session_factory.begin() as session:
        reminder = await session.get(Reminder, reminder_id)
        return reminder


async def select_users_all() -> list[User]:
    """
    Возвращает список объектов всех пользователей
    """
    async with session_factory.begin() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users


async def select_reminders_for_me(telegram_id: int) -> list[Reminder]:
    """
    Возвращает список напоминаний созданных для пользователя по telegram id
    """
    async with session_factory.begin() as session:
        stmt = select(Reminder).join(ReminderUser, ReminderUser.reminder_id == Reminder.id) \
            .join(User, ReminderUser.user_id == User.id) \
            .where(User.telegram_id == telegram_id, ReminderUser.status.is_(False))
        result = await session.execute(stmt)
        reminders = result.scalars().all()
        return reminders


async def select_my_reminders(telegram_id: int) -> list[Reminder]:
    """
    Возвращает список напоминаний созданных пользователем, по telegram id
    """
    async with session_factory.begin() as session:
        stmt = select(Reminder).join(User).where(User.telegram_id == telegram_id,
                                                 Reminder.status.is_(False))
        result = await session.execute(stmt)
        reminder = result.scalars().all()
        return reminder


async def select_groups_with_user(telegram_id: int) -> list[Group]:
    """
    Возвращает группы, в которых состоит пользователь
    """
    async with session_factory.begin() as session:
        stmt = select(Group).join(GroupUser).join(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        groups = result.scalars().all()
        return groups


async def select_users_on_groups(groups_id: list) -> list[User]:
    """
    Возвращает пользователей, которые входят в группу
    """
    async with session_factory.begin() as session:
        stmt = select(User).join(GroupUser).where(GroupUser.group_id.in_(groups_id)).distinct()
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users


async def select_users_on_reminder(reminder_id: int) -> list[User]:
    """
    Возвращает пользователей, которым создано напоминание
    """
    async with session_factory.begin() as session:
        stmt = select(User).join(ReminderUser, ReminderUser.user_id == User.id)\
            .where(ReminderUser.reminder_id == reminder_id)
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users


async def insert_groups_users(telegram_id: int, titles_groups: list[str]) -> None:
    """
    Добавляет в базу данных запись в таблицу хранящую пользователей, которые входят в группы,
    перед добавлением удаляет все прошлые записи
    """
    async with session_factory.begin() as session:
        user = await select_user(telegram_id)
        delete_stmt = delete(GroupUser).where(GroupUser.user_id == user.id)
        await session.execute(delete_stmt)
        for group_title in titles_groups:
            select_stmt = select(Group).where(Group.title == group_title)
            result = await session.execute(select_stmt)
            group = result.scalar_one()
            stmt = insert(GroupUser).values(user_id=user.id, group_id=group.id)
            await session.execute(stmt)


async def insert_reminder(reminder: Reminder, users_id: set) -> Reminder:
    """
    Добавляет напоминание и запись о напоминании для пользователей в базу данных
    """
    async with session_factory.begin() as session:
        session.add(reminder)
        await session.flush()
        for user in users_id:
            reminders_users = ReminderUser(
                user_id=user,
                reminder_id=reminder.id,
            )
            session.add(reminders_users)
    return reminder


async def update_reminder_status_to_done(reminder_id: int, user_id: int) -> None:
    """
    Изменяет статус напоминания на выполнено (True)
    """
    async with session_factory.begin() as session:
        stmt = select(ReminderUser).where(ReminderUser.reminder_id == reminder_id,
                                          ReminderUser.user_id == user_id)
        result = await session.execute(stmt)
        reminder_user: ReminderUser = result.scalar_one()
        reminder_user.status = True


async def select_reminder_users_status(reminder_id: int) -> list[(ReminderUser.user_id, ReminderUser.status)]:
    """
    Возвращает список пользователей и отметку о статусе выполнения напоминания
    """
    async with session_factory.begin() as session:
        stmt = select(User.shortname, ReminderUser.status).join_from(ReminderUser, User)\
            .where(ReminderUser.reminder_id == reminder_id)
        result = await session.execute(stmt)
        users = result.all()
        return users


async def delete_reminder(reminder_id: int) -> None:
    """
    Удаляет напоминание
    """
    async with session_factory.begin() as session:
        reminder = await session.get(Reminder, reminder_id)
        await session.delete(reminder)


async def select_reminder_for_send() -> list[Reminder]:
    """
    Возвращает напоминания, которые должны быть сейчас отправлены
    """
    today = dt.datetime.today()
    date = dt.datetime.date(today)
    time = dt.datetime.time(today).replace(second=0, microsecond=0)
    day_week = today.weekday()
    async with session_factory.begin() as session:
        stmt = select(Reminder).where(Reminder.times.any_() == time,
                                      or_(Reminder.dates.any_() == date,
                                          Reminder.days_week.any_() == day_week))
        result = await session.execute(stmt)
        reminders = result.scalars().all()
        return reminders


async def check_reminder_for_completion(reminder_id: int) -> None:
    """
    Проверяет все ли пользователи, завершили выполнение напоминания.
    Если завершили, то устанавливает дату удаления через 3 дня, если прошлая дата была позже
    """
    async with session_factory.begin() as session:
        stmt = select(ReminderUser).where(ReminderUser.reminder_id == reminder_id)
        result = await session.execute(stmt)
        reminder_users = result.scalars().all()
        for ru in reminder_users:
            if ru.status is False:
                return
        reminder = await session.get(Reminder, reminder_id)
        reminder.status = True
        new_time_delete = dt.datetime.date(dt.datetime.today()) + dt.timedelta(days=3)
        if not reminder.date_delete or reminder.date_delete > new_time_delete:
            reminder.date_delete = new_time_delete


async def select_users_for_reminder(reminder_id: int) -> list[User]:
    """
    Возвращает всех пользователей для напоминания
    """
    async with session_factory.begin() as session:
        stmt = select(User).join(ReminderUser).where(ReminderUser.reminder_id == reminder_id)
        result = await session.execute(stmt)
        users = result.scalars().all()
        return users


async def delete_group(group_id: int) -> None:
    async with session_factory.begin() as session:
        group = await session.get(Group, group_id)
        await session.delete(group)


async def delete_user(user_id: int) -> None:
    async with session_factory.begin() as session:
        user = await session.get(User, user_id)
        await session.delete(user)


async def delete_reminder_scheduler() -> None:
    """
    Удаляет напоминания, работает с scheduler
    """
    async with session_factory.begin() as session:
        stmt = delete(Reminder).where(Reminder.date_delete >= dt.date.today())
        await session.execute(stmt)


async def select_creator(reminder_id: int) -> User:
    """
    Возвращает пользователя создавшего напоминание
    """
    async with session_factory.begin() as session:
        stmt = select(User).join(Reminder, Reminder.creator_id == User.id).where(Reminder.id == reminder_id)
        result = await session.execute(stmt)
        user = result.scalar_one()
        return user
