from flask import Blueprint, render_template, request, current_app
from app.models import Product, Category, Brand
from app.extensions import db

catalog_bp = Blueprint('catalog', __name__)


@catalog_bp.route('/')
def product_list():
    page = request.args.get('page', 1, type=int)
    per_page = 6

    # Базовый запрос
    query = Product.query

    # Поиск
    search_query = request.args.get('q', '')
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    # Фильтр по категории
    category_slug = request.args.get('category')
    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug)

    # Пагинация
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = Category.query.all()

    return render_template(
        'catalog/product_list.html',
        page_obj=pagination,
        categories=categories,
        search_query=search_query
    )


@catalog_bp.route('/categories/')
def category_list():
    categories = Category.query.all()
    return render_template('catalog/category_list.html', categories=categories)


@catalog_bp.route('/category/<slug:category_slug>/')
def category_detail(category_slug):
    page = request.args.get('page', 1, type=int)
    per_page = 6

    category = Category.query.filter_by(slug=category_slug).first_or_404()

    query = category.products
    search_query = request.args.get('q', '')
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'catalog/category_detail.html',
        category=category,
        page_obj=pagination,
        search_query=search_query
    )


@catalog_bp.route('/brands/')
def brand_list():
    brands = Brand.query.all()
    return render_template('catalog/brand_list.html', brands=brands)


@catalog_bp.route('/brand/<slug:brand_slug>/')
def brand_detail(brand_slug):
    page = request.args.get('page', 1, type=int)
    per_page = 6

    brand = Brand.query.filter_by(slug=brand_slug).first_or_404()

    query = brand.products
    search_query = request.args.get('q', '')
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'catalog/brand_detail.html',
        brand=brand,
        page_obj=pagination,
        search_query=search_query
    )


@catalog_bp.route('/product/<int:product_id>/')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('catalog/product_detail.html', product=product)