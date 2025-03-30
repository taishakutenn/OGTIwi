from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField, StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField("Nickname", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль",
                             validators=[DataRequired(),
                                         Length(6, 20, "Вы ввели не подходящий пароль"),
                                         EqualTo("retype_password", "Пароли не совпадают")])
    retype_password = PasswordField("Повторите пароль", validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class SettingsForm(FlaskForm):
    name = StringField("Имя")
    surname = StringField("Фамилия")
    nickname = StringField("Никнейм", validators=[DataRequired()])
    about = TextAreaField("Информация о себе")
    submit = SubmitField('Сохранить изменения')