from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен'),
        Length(min=1, max=150, message='Логин должен быть от 1 до 150 символов')
    ])
    email = EmailField('Электронная почта', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email')
    ])
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=8, message='Пароль должен содержать не менее 8 символов')
    ])
    password2 = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message='Подтверждение пароля обязательно'),
        EqualTo('password', message='Пароли должны совпадать')
    ])


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Логин обязателен')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Пароль обязателен')])


class ProfileForm(FlaskForm):
    phone = StringField('Телефон')
    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Допустимы только изображения (jpg, jpeg, png, gif)')
    ])
    bio = TextAreaField('О себе')