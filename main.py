from flask import Flask, render_template, url_for, redirect

from data import db_session
from src.settings import SECRET_KEY  # Получаем секртеный ключ ответа сервера для flask-wtf
from src.user_management import *
from forms.user import LoginForm, RegisterForm # Импортируем классы форм

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


def main():
    db_session.global_init("db/ogti_wi_articles.db")  # Инициилизируем бд
    app.run()


@app.route("/")
@app.route("/index")
def index():
    params = {}
    params["title"] = "OGTIwi"

    return render_template("index.html", **params)


@app.route("/register", methods=["GET", "POST"])
def register():
    form_log = LoginForm()
    form_reg = RegisterForm()

    params = {
        "title": "Авторизация",
        "form_log": form_log,
        "form_reg": form_reg
    }

    # if form_log.validate_on_submit():
    #     return redirect('/index')

    if form_reg.validate_on_submit():
        print("Кнопка))")
        if form_reg.password.data != form_reg.retype_password.data:
            print("Пароли не совпадают")
            return render_template("register.html", **params)

        try:
            create_user(
                form_reg.name.data,
                "avatarurl",
                form_reg.email.data,
                form_reg.password.data,
                "user"
            )
            return redirect('/index')
        except ValueError as e:
            print(f"Ошибка регистрации: {e}")
            params["error_message"] = str(e)  # Передаем сообщение об ошибке в шаблон
            return render_template("register.html", **params)

    return render_template("register.html", **params)


@app.route("/ribbon")
def ribbon():
    params = {}
    params["title"] = "Лента"

    return render_template("ribbon.html", **params)


if __name__ == '__main__':
    main()
