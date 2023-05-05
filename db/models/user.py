from sqlalchemy import Column, String, BigInteger
from sqlalchemy.orm import relationship
from .base import BaseModel

from .group_user import GroupUser
from .reminder_user import ReminderUser
from .reminder import Reminder


class User(BaseModel):
    __tablename__ = 'users'

    telegram_id = Column(BigInteger, unique=True, nullable=True)
    fullname = Column(String, nullable=True)
    shortname = Column(String, nullable=True)
    photo = Column(String)
    telegram_username = Column(String)
    telegram_name = Column(String)

    reminder_groups_users = relationship(GroupUser, cascade='delete, all')
    reminder_reminders_users = relationship(ReminderUser, cascade='delete, all')
    reminder_reminders = relationship(Reminder, cascade='delete, all')

    def __init__(self, telegram_id, fullname, shortname, photo,telegram_username, telegram_name):
        self.telegram_id = telegram_id
        self.fullname = fullname
        self.shortname = shortname
        self.photo = photo
        self.telegram_username = telegram_username
        self.telegram_name = telegram_name
