from data import db_session
from data.users import User
from werkzeug.security import generate_password_hash


def create_user(username, avatar_url, email, password, role, name=None, surname=None, about=None):
    with db_session.create_session() as db_sess:  # Создаём ссесию с базой данных

        if db_sess.query(User).filter(User.username == username).first():
            raise "Пользователь с таким никнеймом уже существует"

        if db_sess.query(User).filter(User.email == email).first():
            raise "На данную почту уже зарегистрирован аккаунт"

        new_user = User(username=username,
                        avatar_url=avatar_url,
                        email=email,
                        hashed_password=generate_password_hash(password),
                        role=role,
                        name=name,
                        surname=surname,
                        about=about)

        db_sess.add(new_user)
        db_sess.commit()


def get_user_info(email):
    with db_session.create_session() as db_sess:
        user_info = db_sess.query(User).filter(User.email == email).first()
        if not user_info:
            return None

        return user_info


def get_username_info(username):
    with db_session.create_session() as db_sess:
        user_info = db_sess.query(User).filter(User.name == username).first()
        if not user_info:
            return None

        return user_info
