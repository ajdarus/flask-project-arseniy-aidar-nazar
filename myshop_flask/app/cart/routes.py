from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Product, Cart, CartItem, Order, OrderItem
from .forms import OrderForm
import uuid

cart_bp = Blueprint('cart', __name__)


def get_or_create_cart():
    """Возвращает корзину для пользователя или сессии."""
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        return cart
    else:
        if 'session_key' not in session:
            session['session_key'] = str(uuid.uuid4())
        session_key = session['session_key']
        cart = Cart.query.filter_by(session_key=session_key).first()
        if not cart:
            cart = Cart(session_key=session_key)
            db.session.add(cart)
            db.session.commit()
        return cart


@cart_bp.route('/')
def cart_detail():
    cart = get_or_create_cart()
    items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in items)
    return render_template('cart/cart_detail.html', items=items, total_price=total_price)


@cart_bp.route('/add/<int:product_id>/')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = get_or_create_cart()

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'Товар "{product.name}" добавлен в корзину.', 'success')
    return redirect(url_for('cart.cart_detail'))


@cart_bp.route('/update/<int:item_id>/', methods=['POST'])
def update_cart_item(item_id):
    cart = get_or_create_cart()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()

    quantity = int(request.form.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        db.session.commit()
    else:
        db.session.delete(item)
        db.session.commit()

    return redirect(url_for('cart.cart_detail'))


@cart_bp.route('/remove/<int:item_id>/')
def remove_from_cart(item_id):
    cart = get_or_create_cart()
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()

    db.session.delete(item)
    db.session.commit()
    flash('Товар удалён из корзины.', 'info')
    return redirect(url_for('cart.cart_detail'))


@cart_bp.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    cart = get_or_create_cart()
    items = cart.items.all()

    if not items:
        flash('Корзина пуста.', 'warning')
        return redirect(url_for('cart.cart_detail'))

    initial_data = {}
    if current_user.is_authenticated:
        initial_data = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'email': current_user.email,
        }
        if current_user.profile and current_user.profile.phone:
            initial_data['phone'] = current_user.profile.phone

    form = OrderForm(data=initial_data)
    total_price = sum(item.product.price * item.quantity for item in items)

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            status='new',
            total=total_price
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)

        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()

        flash('Заказ успешно оформлен!', 'success')
        return redirect(url_for('cart.order_completed', order_id=order.id))

    return render_template('cart/checkout.html', form=form, items=items, total_price=total_price)


@cart_bp.route('/completed/<int:order_id>/')
def order_completed(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('cart/order_completed.html', order=order)