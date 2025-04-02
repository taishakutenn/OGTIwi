import base64

from flask import Flask, render_template, url_for, redirect, request, jsonify, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from data import db_session
from data.db_session import create_session
from data.news_to_tags import NewsToTags
from data.demands import Demand
from data.tags import Tag
from forms.article import CreateArticle
from src.settings import SECRET_KEY  # Получаем секртеный ключ ответа сервера для flask-wtf
from src.user_management import *
from src.article_management import *
from forms.user import LoginForm, RegisterForm, SettingsForm  # Импортируем классы форм

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

    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        is_creator = db_sess.query(Demand).filter(Demand.user_id == current_user.id).first()
        params["is_creator"] = is_creator
    else:
        params["is_creator"] = False

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

    total_articles = db_sess.query(Article).count()  # Общее количество статей
    max_page = (total_articles + articles_per_page - 1) // articles_per_page  # Расчёт количества страниц

    # Словарь для хранения параметров
    params = {
        "title": "Лента",
        "articles": [],
        "page": page,
        "max_page": max_page
    }

    # Для каждой статьи получаем её теги
    for article in articles:
        article_to_tags = db_sess.query(NewsToTags).filter(NewsToTags.article_id == article.id).all()

        # Получаем имена тегов для текущей статьи
        tags = [tag.tag.name for tag in article_to_tags]

        # Добавляем статью и её теги в параметры
        params["articles"].append({
            "article": article,
            "tags": tags,
        })

    # Передаем параметры в шаблон или обработчик
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


@app.route("/upload_avatar", methods=["POST"])
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    # Читаем бинарные данные файла
    binary_data = file.read()

    # Преобразуем бинарные данные в Base64
    base64_data = base64.b64encode(binary_data).decode('utf-8')

    # Создаём ссесию
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == current_user.id).first() # Берём нужного пользователя
    # Загружаем аватар в базу данных
    user.binary_avatar = base64_data
    db_sess.commit()

    return jsonify({'message': 'Файл успешно загружен'})


@app.context_processor
def inject_user_avatar():
    """
    Добавляет данные об аватаре пользователя в контекст всех шаблонов.
    """
    if current_user.is_authenticated:
        user_avatar = current_user.binary_avatar  # Получаем Base64 строку изображения
    else:
        user_avatar = None  # Если пользователь не авторизован

    return dict(user_avatar=user_avatar)


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

        foreign_avatar = foreign_user.binary_avatar
        params["foreign_avatar"] = foreign_avatar

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

    db_sess = db_session.create_session()
    article_to_tags = db_sess.query(NewsToTags).filter(NewsToTags.article_id == article_id).all()

    params = {"article": article,
              "tags": [value.tag.name for count, value in enumerate(article_to_tags) if count < 5],
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
    existing_tags_list = db_sess.query(Tag).limit(5).all()

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


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if not current_user.is_authenticated:
        return redirect("/login")

    # Создаем форму с начальными значениями из current_user
    form = SettingsForm(obj=current_user)

    params = {
        "title": "Настройки",
        "form": form
    }

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        # Проверка уникальности никнейма
        if form.username.data != current_user.username:
            is_nickname = db_sess.query(User.username).filter(User.username == form.nickname.data).first()
            if is_nickname and is_nickname[0] != current_user.username:
                print("Пользователь с таким ником уже существует")
                return render_template("settings.html", **params)
            else:
                user.username = form.nickname.data

        if form.name.data != current_user.name:
            user.name = form.name.data

        if form.surname.data != current_user.surname:
            user.surname = form.surname.data

        if form.about.data != current_user.about:
            user.about = form.about.data

        # Сохранение изменений в базе данных
        db_sess.commit()

        return render_template("settings.html", **params)

    return render_template("settings.html", **params)


@app.route("/admin/confirmation")
def confirmation():
    return "Страница подтверждения возможности создания статей"


@app.route("/article/<int:article_id>/edit", methods=["GET", "POST"])
def edit_article(article_id):
    if not current_user.is_authenticated:  # Если пользователь не авторизован
        return redirect("/login")

    # Получаем данные о статье
    db_sess = db_session.create_session()
    article = db_sess.query(Article).filter(Article.id == article_id).first()

    # Проверяем, существует ли статья
    if not article:
        return "Такой статьи не существует", 404

    # Проверяем, является ли текущий пользователь создателем статьи
    if not article.user.id == current_user.id:
        return "Отказано в доступе", 404

    form = CreateArticle()

    params = {"title": "Редактирование статьи",
              "form": form}

    return render_template("create_article.html", **params)


@app.route("/<string:username>/all_articles")
def all_user_articles(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()

    if not user:
        return "Такого пользователя не существует", 404

    # Получаем статьи пользователя через связь
    articles = user.articles  # Это список статей, связанных с пользователем

    params = {
        "title": f"Статьи {username}",
        "articles": articles,
        "username": username
    }

    return render_template("user_articles.html", **params)


@app.route("/send_confirmation", methods=["POST"])
def send_confirmation():
    try:
        # Создаём сессию
        db_sess = db_session.create_session()
        is_send = db_sess.query(Demand).filter(Demand.user_id == current_user.id).all()

        if is_send:
            for data in is_send:
                if data.status == "pending" or data.status == "approved":
                    return jsonify({"message": "Вы уже делали запрос"}), 400

        # Создаём запрос
        demand = Demand()
        demand.user_id = current_user.id
        db_sess.add(demand)
        db_sess.commit()

        # Возвращаем успешный ответ
        return jsonify({"message": "Запрос успешно отправлен"}), 200

    except Exception as e:
        # Возвращаем сообщение об ошибке
        return jsonify({"message": f"Произошла ошибка: {str(e)}"}), 500


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()  # Получаем поисковый запрос из параметра GET
    page = request.args.get('page', default=1, type=int)  # Номер страницы

    if not query:
        return render_template('ribbon.html', articles=[], query=query, page=page, max_page=None)

    db_sess = create_session()

    # Количество статей на странице
    articles_per_page = 6
    offset = (page - 1) * articles_per_page  # Сколько записей нужно пропустить

    # Ищем статьи, где заголовок, текст или теги содержат поисковый запрос
    filtered_articles = (
        db_sess.query(Article)
        .select_from(Article)
        .join(NewsToTags)
        .join(Tag)
        .filter(
            (Article.title.ilike(f'%{query}%')) |  # Поиск в заголовке
            (Article.article_text.ilike(f'%{query}%')) |  # Поиск в тексте статьи
            (Tag.name.ilike(f'%{query}%'))  # Поиск в тегах
        )
        .distinct()
    )

    # Общее количество найденных статей
    total_articles = filtered_articles.count()

    # Расчёт общего количества страниц
    max_page = (total_articles + articles_per_page - 1) // articles_per_page

    # Получаем статьи для текущей страницы
    articles_db = (
        filtered_articles
        .order_by(Article.id.desc())  # Сортируем по убыванию ID
        .offset(offset)
        .limit(articles_per_page)
        .all()
    )

    # Преобразуем данные в нужный формат
    articles = []
    for article in articles_db:
        # Получаем теги для текущей статьи
        article_to_tags = db_sess.query(NewsToTags).filter(NewsToTags.article_id == article.id).all()
        tags = [tag.tag.name for tag in article_to_tags]

        # Добавляем статью и её теги в список
        articles.append({
            "article": article,
            "tags": tags,
        })
    params = {"articles": articles,
              "query": query,
              "page": page,
              "max_page": max_page,
              "title": "Поиск"}

    # Передаем параметры в шаблон
    return render_template('ribbon.html', **params)


if __name__ == '__main__':
    main()
