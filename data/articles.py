import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    __tablename__ = 'articles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # Заголовок статьи
    preview = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Краткое описание
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)  # ID автора
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # Дата создания
    updated_date = sqlalchemy.Column(sqlalchemy.DateTime, onupdate=datetime.datetime.now, nullable=True)  # Дата обновления
    file_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Путь к файлу с текстом статьи
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)  # Теги для фильтрации
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # Количество просмотров

    user = orm.relationship('User')


    def __repr__(self):
        return (f"{self.id} - {self.title} - {self.preview} - {self.author_id} - {self.created_date} "
                f"{self.updated_date} - {self.file_path} - {self.tags} - {self.views}")