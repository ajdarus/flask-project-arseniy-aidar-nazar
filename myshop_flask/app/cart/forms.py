from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email


class OrderForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(message='Имя обязательно')])
    last_name = StringField('Фамилия', validators=[DataRequired(message='Фамилия обязательна')])
    email = EmailField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email')
    ])
    phone = StringField('Телефон', validators=[DataRequired(message='Телефон обязателен')])
    address = TextAreaField('Адрес доставки', validators=[DataRequired(message='Адрес обязателен')])