from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, FileField, FloatField
from wtforms.validators import DataRequired, Length
from app.models import Movie

class ChooseGenre(FlaskForm):
    genre = StringField('Введите желаемый жанр:', validators=[DataRequired()], default='Horror')
    submit = SubmitField('Найти')

class ChooseUser(FlaskForm):
    user = IntegerField('Введите существующий id пользователя для проверки:', validators=[DataRequired()], default=1)
    submit = SubmitField('Дать рекомендации')

class PollReview(FlaskForm):
    title = StringField('Введите название фильма:', validators=[DataRequired()])
    year = StringField('Введите год выпуска фильма:', validators=[DataRequired()])
    analyzer = BooleanField ('Быстрый анализ отзыва (только английский)')
    review = TextAreaField('Введите отзыв:', validators=[DataRequired(), Length(min=1, max=300)],  render_kw={'cols' : 10, 'rows': 10})
    submit = SubmitField('Отправить отзыв')

class TextSeniment(FlaskForm):
    review = TextAreaField('Введите отзыв:', validators=[DataRequired(), Length(min=1, max=300)],  render_kw={'cols' : 10, 'rows': 10})
    analyzer = BooleanField ('Быстрый анализ (только английский)')
    submit = SubmitField('Отправить')

class BackSentiment(FlaskForm):
    review_test =TextAreaField('Введите отзыв:', validators=[DataRequired(), Length(min=1, max=300)],  render_kw={'cols' : 10, 'rows': 10})
    rating_sent = FloatField('Подтвердите или исправьте оценку:')
    submit_false = SubmitField('Отправить')

class DataRecommend(FlaskForm):
    #ratings = FileField('Загрузить набор данных',  validators=[DataRequired()])
    scale_bottom = FloatField('Введите нижнюю границу рейтинговой шкалы:', validators=[DataRequired()], default=0)
    scale_top = FloatField('Введите верхнюю границу рейтинговой шкалы:', validators=[DataRequired()], default=5)
    round_rating = BooleanField ('Округление рейтингов (2.85 -> 3.0)')
    analyzer = BooleanField ('Быстрый анализ (только английский)')
    submit = SubmitField('Отправить')