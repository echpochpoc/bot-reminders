from sqlalchemy import Column, Integer, ForeignKey
from .base import BaseModel


class ReminderUser(BaseModel):
    __tablename__ = 'reminders_users'

    user_id = Column(Integer, ForeignKey('users.id'))
    reminder_id = Column(Integer, ForeignKey('reminders.id'))

    def __init__(self, user_id, reminder_id):
        self.user_id = user_id
        self.reminder_id = reminder_id
