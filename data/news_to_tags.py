import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class NewsToTags(SqlAlchemyBase):
    __tablename__ = 'news_to_tags'

    article_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('articles.id'),
        primary_key=True
    )
    tag_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('tags.id'),
        primary_key=True
    )

    # Отношения с таблицами
    article = relationship("Article", back_populates="tags")
    tag = relationship("Tag", back_populates="articles")