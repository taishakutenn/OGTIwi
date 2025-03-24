from flask import Flask, render_template, url_for, redirect, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from data import db_session
from data.db_session import create_session
from data.news_to_tags import NewsToTags
from data.tags import Tag
from forms.article import CreateArticle
from src.settings import SECRET_KEY  # Получаем секртеный ключ ответа сервера для flask-wtf
from src.user_management import *
from src.article_management import *
from forms.user import LoginForm, RegisterForm  # Импортируем классы форм

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)

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


@app.route("/register", methods=["GET", "POST"])
def register():
    form_reg = RegisterForm()
    params = {}
    params["title"] = "Регистрация"
    params["form_reg"] = form_reg

    if form_reg.validate_on_submit():
        if form_reg.password.data != form_reg.retype_password.data:
            params["error_message"] = "Пароли не совпадают"
            return render_template("register.html", **params)

        try:
            create_user(
                form_reg.name.data,
                form_reg.email.data,
                form_reg.password.data,
                "user"
            )
            return redirect('/login')
        except ValueError as e:
            params["error_message"] = str(e)
            return render_template("register.html", **params)

    return render_template("register.html", **params)


@app.route("/login", methods=["GET", "POST"])
def login():
    params = {}
    form_log = LoginForm()
    params["title"] = "Авторизация"

    if form_log.validate_on_submit():
        user = get_user_info(email=form_log.email.data)
        if not user:
            return render_template("login.html", form_log=form_log, error_message="Такого пользователя не существует")

        if not user.check_password(form_log.password.data):
            return render_template("login.html", form_log=form_log, error_message="Неверный пароль")

        # Авторизуем пользователя
        login_user(user, remember=True)
        return redirect('/index')

    return render_template("login.html", form_log=form_log)


@login_manager.user_loader # загружаем пользователя при запуске
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout') # забываем пользователя при вызове
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/ribbon")
def ribbon():
    page = request.args.get('page', default=1, type=int)

    articles_per_page = 6 # Статей на странице
    offset = (page - 1) * articles_per_page # Сколько записей нужно пропустить в бд для данной страницы

    db_sess = db_session.create_session()
    # По умолчанию получаем последние 6 статей
    articles = db_sess.query(Article).order_by(Article.id.desc()).offset(offset).limit(articles_per_page).all()

    params = {}
    params["title"] = "Лента"
    params["articles"] = articles

    return render_template("ribbon.html", **params)


@app.route("/account")
def account():
    params = {}
    params["my_profile"] = True
    params["title"] = "Личный кабинет"
    params["nickname"] = current_user.username
    params["email"] = current_user.email
    params["created_date"] = current_user.created_date
    params["last_articles"] = current_user.articles

    if current_user.name:
        params["name"] = current_user.name
    if current_user.surname:
        params["surname"] = current_user.surname

    if not current_user:
        return redirect("/register")

    return render_template("account.html", **params)


@app.route("/account/<string:username>")
def foreign_account(username):
    try: # Проверяем, существует ли пользователь с таким никнеймом
        foreign_user = get_user_info(username=username)

        if foreign_user.id == current_user.id:
            return redirect("/account") # Если попытались по этому пути найти свой профиль и залогинены - отправляем на свой аккаунт

        params = {}
        params["my_profile"] = False
        params["title"] = foreign_user.username
        params["nickname"] = foreign_user.username
        params["email"] = foreign_user.email
        params["created_date"] = foreign_user.created_date
        params["last_articles"] = foreign_user.articles

        if current_user.name:
            params["name"] = foreign_user.name
        if current_user.surname:
            params["surname"] = foreign_user.surname

        return render_template("account.html", **params)

    except Exception as e:
        print(e)
        return "Пользователь не найден", 404


@app.route("/article/<int:article_id>")
def article(article_id):
    article = get_article(article_id)

    if not article:
        return "Статья не найдена", 404

    params = {"article": article,
              "title": article.title}

    return render_template("article.html", **params)


@app.route('/create_article', methods=['GET', 'POST'])
def create_article():
    if not current_user.is_authenticated:  # Если пользователь не авторизован
        return redirect("/login")

    form = CreateArticle()

    params = {
        "title": "Создание статьи",
        "form": form
    }

    db_sess = db_session.create_session()
    existing_tags_list = db_sess.query(Tag).all()

    # Добавляем чекбоксы для существующих тегов
    for tag in existing_tags_list:
        form.existing_tags.append_entry()  # Добавляем новое поле
        form.existing_tags[-1].label.text = tag.name  # Устанавливаем метку для чекбокса

    if form.validate_on_submit():
        try:
            title = form.title.data
            preview = form.preview.data
            content = form.content.data

            # Получаем выбранные теги
            selected_tags = [
                existing_tags_list[i].name for i, checkbox in enumerate(form.existing_tags)
                if checkbox.data
            ]

            # Получаем новые теги
            new_tags = [tag.data.strip() for tag in form.new_tags if tag.data.strip()]

            # Создаём статью
            article = Article(
                author_id=current_user.id,
                title=title,
                preview=preview,
                article_text=content
            )
            db_sess.add(article)
            db_sess.commit()  # Сохраняем статью, чтобы получить её id

            # Добавляем новые теги
            existing_tag_names = {tag.name for tag in db_sess.query(Tag).all()}  # Множество существующих тегов
            for tag_name in new_tags:
                if tag_name and tag_name not in existing_tag_names:
                    tag = Tag(name=tag_name)
                    db_sess.add(tag)
                    existing_tag_names.add(tag_name)  # Обновляем множество
            db_sess.commit()  # Сохраняем новые теги

            # Создаём связи между статьёй и тегами
            for tag_name in selected_tags + new_tags:  # Объединяем выбранные и новые теги
                tag = db_sess.query(Tag).filter(Tag.name == tag_name).first()
                if tag:
                    news_to_tags = NewsToTags(article_id=article.id, tag_id=tag.id)
                    db_sess.add(news_to_tags)

            db_sess.commit()  # Коммитим все изменения
            return redirect(f"/article/{article.id}")

        except Exception as e:
            db_sess.rollback()  # Откатываем изменения в случае ошибки
            return render_template('create_article.html', error="Произошла ошибка при создании статьи.", **params)

    return render_template('create_article.html', **params)


if __name__ == '__main__':
    main()
