from sqlalchemy import Column, String
from .base import BaseModel


class Group(BaseModel):
    __tablename__ = 'groups'

    title = Column(String, nullable=True, unique=True)
    description = Column(String)

    def __init__(self, title, description):
        self.title = title
        self.description = description
