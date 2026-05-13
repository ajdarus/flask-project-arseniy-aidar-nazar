from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .extensions import db
from .models import User, Profile, Category, Brand, Product, Cart, CartItem, Order, OrderItem
from flask_admin.form import ImageUploadField


class CategoryView(ModelView):
    column_labels = {
        'name': 'Название',
        'slug': 'URL-идентификатор',
        'product_count': 'Товаров',
        'products': 'Товары',
    }
    column_list = ('name', 'slug')
    column_searchable_list = ('name',)
    form_columns = ('name', 'slug')
    form_labels = {
        'name': 'Название категории',
        'slug': 'URL-идентификатор',
    }

    def product_count(self, view, context, model, name):
        return model.products.count()

    column_formatters = {
        'product_count': product_count
    }


class BrandView(ModelView):
    column_labels = {
        'name': 'Название',
        'slug': 'URL-идентификатор',
        'country': 'Страна',
        'description': 'Описание',
    }
    column_list = ('name', 'slug', 'country')
    column_searchable_list = ('name', 'country')
    column_filters = ('country',)
    form_columns = ('name', 'slug', 'country', 'description')
    form_labels = {
        'name': 'Название бренда',
        'slug': 'URL-идентификатор',
        'country': 'Страна',
        'description': 'Описание',
    }


class ProductView(ModelView):
    column_labels = {
        'name': 'Название',
        'price': 'Цена',
        'category': 'Категория',
        'brand': 'Бренд',
        'created_at': 'Дата создания',
        'description': 'Описание',
        'picture': 'Изображение',
    }
    column_list = ('name', 'price', 'category', 'brand', 'created_at')
    column_searchable_list = ('name', 'description')
    column_filters = ('category', 'brand', 'created_at')
    form_columns = ('name', 'price', 'description', 'picture', 'category', 'brand')
    form_labels = {
        'name': 'Название товара',
        'price': 'Цена',
        'description': 'Описание',
        'picture': 'Изображение',
        'category': 'Категория',
        'brand': 'Бренд',
    }
    column_default_sort = ('created_at', True)


    form_overrides = {
        'picture': ImageUploadField
    }

    form_args = {
        'picture': {
            'label': 'Изображение товара',
            'base_path': 'app/static/uploads/products/',
            'relative_path': 'uploads/products/',
            'max_size': (500, 500, True),  # макс. размер, авто-обрезка
            'allowed_extensions': {'jpg', 'jpeg', 'png', 'gif'},
        }
    }


class UserView(ModelView):
    column_labels = {
        'username': 'Логин',
        'email': 'Email',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'password_hash': 'Пароль',
    }
    column_list = ('username', 'email', 'first_name', 'last_name')
    column_searchable_list = ('username', 'email')
    form_columns = ('username', 'email', 'first_name', 'last_name', 'password_hash')
    form_labels = {
        'username': 'Логин',
        'email': 'Email',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
    }


class ProfileView(ModelView):
    column_labels = {
        'user': 'Пользователь',
        'phone': 'Телефон',
        'avatar': 'Аватар',
        'bio': 'О себе',
    }
    column_list = ('user', 'phone')
    form_columns = ('user', 'phone', 'avatar', 'bio')
    form_labels = {
        'user': 'Пользователь',
        'phone': 'Телефон',
        'avatar': 'Аватар',
        'bio': 'О себе',
    }


class OrderView(ModelView):
    column_labels = {
        'id': '№',
        'user': 'Пользователь',
        'customer_name': 'Покупатель',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'email': 'Email',
        'phone': 'Телефон',
        'address': 'Адрес доставки',
        'created_at': 'Дата создания',
        'updated_at': 'Дата обновления',
        'status': 'Статус',
        'total': 'Сумма',
    }
    column_list = ('id', 'customer_name', 'email', 'created_at', 'status', 'total')
    column_searchable_list = ('first_name', 'last_name', 'email')
    column_filters = ('status', 'created_at')
    form_columns = ('first_name', 'last_name', 'email', 'phone', 'address', 'status')
    form_labels = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'email': 'Email',
        'phone': 'Телефон',
        'address': 'Адрес доставки',
        'status': 'Статус',
    }

    def _customer_name(view, context, model, name):
        return f'{model.first_name} {model.last_name}'

    column_formatters = {
        'customer_name': _customer_name
    }


def init_admin(app):
    admin = Admin(
        app,
        name='MyShop Admin',
        template_mode='bootstrap4'
    )
    admin.add_view(CategoryView(Category, db.session, name='Категории'))
    admin.add_view(BrandView(Brand, db.session, name='Бренды'))
    admin.add_view(ProductView(Product, db.session, name='Товары'))
    admin.add_view(UserView(User, db.session, name='Пользователи'))
    admin.add_view(ProfileView(Profile, db.session, name='Профили'))
    admin.add_view(OrderView(Order, db.session, name='Заказы'))