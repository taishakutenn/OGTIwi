import os

from data import db_session
from data.users import User
from werkzeug.security import generate_password_hash


def create_user(username, avatar_url, email, password, role, binary_avatar=None, about=None):
    with db_session.create_session() as db_sess:  # Создаём ссесию с базой данных

        if db_sess.query(User).filter(User.username == username).first():
            raise ValueError("Пользователь с таким никнеймом уже существует")

        if db_sess.query(User).filter(User.email == email).first():
            raise ValueError("На данную почту уже зарегистрирован аккаунт")

        new_user = User(username=username,
                        avatar_url=avatar_url,
                        email=email,
                        hashed_password=generate_password_hash(password),
                        role=role,
                        about=about)

        db_sess.add(new_user)
        db_sess.commit()

        user_id = new_user.id
        base_directory = "users"  # Базовая директория для пользователей
        user_directory = os.path.join(base_directory, f"user-{user_id}")
        articles_directory = os.path.join(user_directory, "articles")

        # Создаем папки, если они не существуют
        os.mkdir(user_directory)
        os.mkdir(articles_directory)

        """Надо пещё прописать получение и добавление аватарки"""


def get_user_info(id=None, email=None):
    with db_session.create_session() as db_sess:
        if not (id or email):
            raise ValueError("Необходимо передать хотя бы один из параметров: id или email")

        if id:
            user_info = db_sess.query(User).filter_by(id=id).first()
        else:
            user_info = db_sess.query(User).filter_by(email=email).first()

        if not user_info:
            raise ValueError("Такого пользователя не существует")

        return {
            "id": user_info.id,
            "username": user_info.username,
            "email": user_info.email,
            "role": user_info.role,
            "name": user_info.name,
            "surname": user_info.surname,
            "about": user_info.about
        }


# Функция для получения всех статей данного пользователя
def get_all_articles(id=None, email=None):
    with db_session.create_session() as db_sess:
        if not (id or email):
            raise ValueError("Необходимо передать хотя бы один из параметров: id или email")

        if id:
            user_info = db_sess.query(User).filter_by(id=id).first()
        else:
            user_info = db_sess.query(User).filter_by(email=email).first()

        if not user_info:
            raise ValueError("Такого пользователя не существует")

        articles_list = [
            {
                "id": article.id,
                "title": article.title,
                "preview": article.preview,
                "content": article.content,
                "created_date": article.created_date
            }
            for article in user_info.articles
        ]

        return articles_list

