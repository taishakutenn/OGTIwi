import os

from sqlalchemy import desc

from data import db_session
from data.articles import Article

def create_article(author_id, title, preview, tags, article_text):
    with db_session.create_session() as db_sess:
        # Определяем пути к директориям
        base_directory = "users"  # Базовая директория для пользователей
        user_directory = os.path.join(base_directory, f"user-{author_id}")
        articles_directory = os.path.join(user_directory, "articles")

        # Создаем новый объект статьи без file_path
        new_article = Article(
            author_id=author_id,
            title=title,
            preview=preview,
            tags=tags
        )

        # Добавляем статью в базу данных
        db_sess.add(new_article)
        db_sess.commit()

        # Получаем ID статьи после коммита
        article_id = new_article.id

        # Создаем путь к файлу с использованием ID статьи
        file_name = f"article-{article_id}.txt"
        file_path = os.path.join(articles_directory, file_name)

        # Записываем текст статьи в файл
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(article_text)

        # Обновляем запись в базе данных, добавляя путь к файлу
        new_article.file_path = file_path
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
                "file_path": article.file_path
            }
            for article in articles
        ]

        return articles_list