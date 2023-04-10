from sqlalchemy import Column, Integer, ForeignKey
from .base import BaseModel


class GroupUser(BaseModel):
    __tablename__ = 'groups_users'

    user_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    def __init__(self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id
