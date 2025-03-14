import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Notification(SqlAlchemyBase):
    __tablename__ = 'notifications'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)  # ID пользователя
    message = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # Текст уведомления
    is_read = sqlalchemy.Column(sqlalchemy.Boolean, default=False)  # Прочитано ли уведомление
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # Дата создания

    user = orm.relationship('User')

    def __repr__(self):
        return f"{self.id} - {self.user_id} - {self.message} - {self.is_read} - {self.created_date}"