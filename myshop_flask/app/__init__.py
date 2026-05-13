from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from werkzeug.routing import BaseConverter


class SlugConverter(BaseConverter):
    """Конвертер для slug-полей (буквы, цифры, дефисы, подчёркивания)"""
    regex = r'[a-zA-Z0-9_-]+'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Регистрируем конвертер slug
    app.url_map.converters['slug'] = SlugConverter

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'users.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'

    # user_loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Создаём все таблицы
    with app.app_context():
        db.create_all()

    # Flask-Admin
    from .admin import init_admin
    init_admin(app)

    # Регистрация Blueprint'ов
    from .catalog.routes import catalog_bp
    from .users.routes import users_bp
    from .cart.routes import cart_bp

    app.register_blueprint(catalog_bp)
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(cart_bp, url_prefix='/cart')

    return app