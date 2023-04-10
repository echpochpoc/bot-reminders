from sqlalchemy import Column, String, BigInteger
from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    telegram_id = Column(BigInteger, unique=True, nullable=True)
    fullname = Column(String, nullable=True)
    shortname = Column(String, nullable=True)
    photo = Column(String)
    telegram_username = Column(String)
    telegram_name = Column(String)

    def __init__(self, telegram_id, fullname, shortname, photo,telegram_username, telegram_name):
        self.telegram_id = telegram_id
        self.fullname = fullname
        self.shortname = shortname
        self.photo = photo
        self.telegram_username = telegram_username
        self.telegram_name = telegram_name
