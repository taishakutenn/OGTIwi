import os

from sqlalchemy import desc

from data import db_session
from data.articles import Article

def create_article(author_id, title, preview, tags, article_text):
    with db_session.create_session() as db_sess:
        new_article = Article(
            author_id=author_id,
            title=title,
            preview=preview,
            tags=tags,
            article_text=article_text
        )

        # Добавляем статью в базу данных
        db_sess.add(new_article)
        db_sess.commit()


def get_last_articles():
    with db_session.create_session() as db_sess:
        articles = db_sess.query(Article).order_by(desc(Article.id)).limit(6).all()

        articles_list = [
            {
                "id": article.id,
                "title": article.title,
                "preview": article.preview,
                "tags": article.tags,
                "created_date": article.created_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for article in articles
        ]

        return articles_list