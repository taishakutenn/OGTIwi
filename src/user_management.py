from data import db_session
from data.users import User
from werkzeug.security import generate_password_hash


def create_user(id, username, avatar_url, email, password, role, name, surname, about=None):
    with db_session.create_session() as db_sess:  # Создаём ссесию с базой данных

        if db_sess.query(User).filter(User.username == username).first():
            raise "Пользователь с таким никнеймом уже существует"

        if db_sess.query(User).filter(User.email == email).first():
            raise "На данную почту уже зарегистрирован аккаунт"

        new_user = User(id=id,
                        username=username,
                        avatar_url=avatar_url,
                        email=email,
                        hashed_password=generate_password_hash(password),
                        role=role,
                        name=name,
                        surname=surname,
                        about=about)

        db_sess.add(new_user)
        db_sess.commit()


def get_user_info(id):
    with db_session.create_session() as db_sess:
        user_info = db_sess.query(User).filter(User.id == id).first()
        if not user_info:
            raise "Такого пользователя не существует"

        return user_info
