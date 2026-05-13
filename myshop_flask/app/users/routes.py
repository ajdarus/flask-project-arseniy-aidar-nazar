import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import User, Profile
from .forms import RegistrationForm, LoginForm, ProfileForm

users_bp = Blueprint('users', __name__)


@users_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.product_list'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Проверка уникальности
        if User.query.filter_by(username=form.username.data).first():
            flash('Пользователь с таким логином уже существует.', 'danger')
            return render_template('users/register.html', form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash('Пользователь с таким email уже существует.', 'danger')
            return render_template('users/register.html', form=form)

        # Создание пользователя
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # чтобы получить user.id

        # Создание профиля
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        # Автоматический вход
        login_user(user)
        flash('Регистрация прошла успешно! Добро пожаловать!', 'success')
        return redirect(url_for('catalog.product_list'))

    return render_template('users/register.html', form=form)


@users_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.product_list'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль.', 'danger')
            return render_template('users/login.html', form=form)

        login_user(user)
        flash(f'Добро пожаловать, {user.username}!', 'success')

        # Перенаправление на страницу, с которой пришли
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('catalog.product_list'))

    return render_template('users/login.html', form=form)


@users_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('catalog.product_list'))


@users_bp.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    profile = current_user.profile
    form = ProfileForm(obj=profile)

    if form.validate_on_submit():
        profile.phone = form.phone.data
        profile.bio = form.bio.data

        # Обработка аватара
        if form.avatar.data:
            # Удаление старого аватара (если был)
            if profile.avatar:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', profile.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Сохранение нового
            filename = secure_filename(form.avatar.data.filename)
            avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            form.avatar.data.save(os.path.join(avatar_dir, filename))
            profile.avatar = filename

        db.session.commit()
        flash('Профиль обновлён.', 'success')
        return redirect(url_for('users.profile'))

    return render_template('users/profile.html', form=form, user=current_user)


@users_bp.route('/password-change/', methods=['GET', 'POST'])
@login_required
def password_change():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')

        if not current_user.check_password(old_password):
            flash('Неверный текущий пароль.', 'danger')
        elif new_password != new_password2:
            flash('Новые пароли не совпадают.', 'danger')
        elif len(new_password) < 8:
            flash('Новый пароль должен содержать не менее 8 символов.', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Пароль успешно изменён.', 'success')
            return redirect(url_for('users.profile'))

    return render_template('users/password_change.html')