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
    article_text = sqlalchemy.Column(sqlalchemy.String, nullable=False) # Текст статьи
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0, index=True)  # Количество просмотров

    user = orm.relationship('User')

    tags = orm.relationship(
        "NewsToTags",
        back_populates="article"
    )


    def __repr__(self):
        return (f"{self.id} - {self.title} - {self.preview} - {self.author_id} - {self.created_date} "
                f"{self.updated_date} - {self.file_path} - {self.tags} - {self.views}")