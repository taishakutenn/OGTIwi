from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FieldList, FormField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


# Форма для одного тега
class TagForm(FlaskForm):
    tag = StringField("Тег", validators=[Length(max=50)])


# Основная форма для статьи
class CreateArticle(FlaskForm):
    title = StringField(
        "Название статьи",
        validators=[DataRequired(), Length(10, 50)]
    )
    preview = TextAreaField(
        "Краткое описание статьи",
        validators=[DataRequired(), Length(100, 500)]
    )
    content = TextAreaField(
        "Текст статьи",
        validators=[DataRequired()]
    )
    existing_tags = FieldList(BooleanField("Существующий тег"), min_entries=0)  # Чекбоксы для существующих тегов
    new_tags = FieldList(StringField("Новый тег", validators=[Length(max=50)]), min_entries=1)  # Новые теги
    submit = SubmitField("Сохранить")