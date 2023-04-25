from sqlalchemy import Column, Integer, ForeignKey, Time, Date, TIMESTAMP, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from .base import BaseModel
from . import ReminderUser


class Reminder(BaseModel):
    __tablename__ = 'reminders'

    creator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    text = Column(String, nullable=True)
    date_delete = Column(TIMESTAMP)
    times = Column(postgresql.ARRAY(Time))
    dates = Column(postgresql.ARRAY(Date))
    days_week = Column(postgresql.ARRAY(Integer),
                       comment='Save the day of the week as an integer, where Monday is 0 and Sunday is 6')
    # delete_all_user_done = Column(TIMESTAMP)
    reminder_user = relationship(ReminderUser, cascade='all')

    def __init__(self, creator_id, text, date_delete, times, dates, days_week):
        self.creator_id = creator_id
        self.text = text
        self.date_delete = date_delete
        self.times = times
        self.dates = dates
        self.days_week = days_week
