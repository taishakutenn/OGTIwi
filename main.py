from flask import Flask, render_template, url_for

from data import db_session
from src.settings import SECRET_KEY  # Получаем секртеный ключ ответа сервера для flask-wtf
from src.user_management import *
from src.article_management import *

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


def main():
    db_session.global_init("db/ogti_wi_articles.db")  # Инициилизируем бд
    app.run()


@app.route("/")
@app.route("/index")
def index():
    params = {}
    articles = get_last_articles()
    params["title"] = "OGTIwi"
    params["articles"] = articles

    return render_template("index.html", **params)


if __name__ == '__main__':
    main()
