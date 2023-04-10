from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP
from .base import BaseModel


class Reminder(BaseModel):
    __tablename__ = 'reminders'

    creator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    text = Column(String, nullable=True)
    date_delete = Column(TIMESTAMP)

    def __init__(self, creator_id, text, date_delete):
        self.creator_id = creator_id
        self.text = text
        self.date_delete = date_delete
