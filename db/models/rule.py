from sqlalchemy import Column, Integer, ForeignKey, Time, Date
from sqlalchemy.dialects import postgresql
from .base import BaseModel


class Rule(BaseModel):
    __tablename__ = 'rules'

    reminder_id = Column(Integer, ForeignKey('reminders.id'), nullable=True)
    times = Column(postgresql.ARRAY(Time))
    dates = Column(postgresql.ARRAY(Date))
    days_week = Column(postgresql.ARRAY(Integer),
                     comment='Save the day of the week as an integer, where Monday is 0 and Sunday is 6')

    def __init__(self, reminder_id, times, dates, days_week):
        self.reminder_id = reminder_id
        self.times = times
        self.dates = dates
        self.days_week = days_week
