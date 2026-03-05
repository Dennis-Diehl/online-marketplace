from flask import render_template, request, redirect, url_for, session
from app import data_access
from app.utils import login_required
from . import bp


@bp.route('/order')
@login_required
def order():
    user_id = session.get('user_id')
    try:
        orders = data_access.get_orders_by_user_id(user_id)
        return render_template('orders/order.html', orders=orders)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/seller_orders')
@login_required
def seller_orders():
    user_id = session.get('user_id')
    try:
        products = data_access.get_products_by_seller_id(user_id)
        return render_template('orders/seller_orders.html', products=products)
    except Exception as err:
        return f"Database error: {err}", 500
