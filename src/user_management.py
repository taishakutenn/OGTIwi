import os

from sqlalchemy.orm import joinedload

from data import db_session
from data.users import User
from werkzeug.security import generate_password_hash


def create_user(username, email, password, role, binary_avatar=None, about=None):
    with db_session.create_session() as db_sess:  # Создаём ссесию с базой данных

        if db_sess.query(User).filter(User.username == username).first():
            raise ValueError("Пользователь с таким никнеймом уже существует")

        if db_sess.query(User).filter(User.email == email).first():
            raise ValueError("На данную почту уже зарегистрирован аккаунт")

        new_user = User(username=username,
                        email=email,
                        hashed_password=generate_password_hash(password),
                        role=role,
                        binary_avatar=binary_avatar,
                        about=about)

        db_sess.add(new_user)
        db_sess.commit()


def get_user_info(id=None, email=None, username=None):

    if not (id or email or username):
        raise ValueError("Необходимо передать хотя бы один из параметров: id, email или username")

    with db_session.create_session() as db_sess:
        query = db_sess.query(User)

        if id:
            query = query.filter_by(id=id)
        if email:
            query = query.filter_by(email=email)
        if username:
            query = query.filter_by(username=username)

        user_info = query.options(joinedload(User.articles)).first()

        if not user_info:
            raise ValueError("Пользователь не найден")

        return user_info


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

