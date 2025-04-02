import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Demand(SqlAlchemyBase):
    __tablename__ = 'requests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)  # ID пользователя
    status = sqlalchemy.Column(sqlalchemy.String, default="pending")  # Статус: "pending", "approved", "rejected"
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.date.today)  # Дата создания запроса
    reviewed_by = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)  # Кто рассмотрел
    reviewed_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)  # Дата рассмотрения
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Комментарий администратора

    def __repr__(self):
        return (f"{self.id} - {self.user_id} - {self.status} - {self.created_date} - {self.reviewed_by}"
                f" - {self.reviewed_date} - {self.comment}")