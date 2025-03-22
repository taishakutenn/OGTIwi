from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class ArticleEdit(FlaskForm):
    pass