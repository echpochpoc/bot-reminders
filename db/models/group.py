from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel

from .group_user import GroupUser


class Group(BaseModel):
    __tablename__ = 'groups'

    title = Column(String, nullable=True, unique=True)
    description = Column(String)

    reminder_groups_users = relationship(GroupUser, cascade='delete, all')

    def __init__(self, title, description):
        self.title = title
        self.description = description
