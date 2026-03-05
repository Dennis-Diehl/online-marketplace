from flask import render_template, request, redirect, url_for, session, flash
from app import data_access
from app.db import get_db_connection
from app.utils import login_required
from . import bp


@bp.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart/cart.html', cart_items=cart_items)


@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if not product:
                flash('Product not found!', 'error')
                return redirect(url_for('products.index'))
            if product['available_copies'] <= 0:
                flash('Product is out of stock!', 'warning')
                return redirect(url_for('products.product_detail', product_id=product_id))
            if product['seller_id'] == session.get('user_id'):
                flash('You cannot add your own product to the cart!', 'warning')
                return redirect(url_for('products.product_detail', product_id=product_id))
            if 'cart' not in session:
                session['cart'] = []
            session['cart'].append(product)
            session.modified = True
            cursor.execute("""
                INSERT INTO ShoppingCarts (user_id, prod_id) VALUES (%s, %s)
            """, (session.get('user_id'), product_id))
            cursor.execute("""
                UPDATE products SET available_copies = available_copies - 1 WHERE product_id = %s
            """, (product_id,))
            conn.commit()
        return redirect(url_for('cart.cart'))
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    cart_items = session.get('cart', [])
    for index, item in enumerate(cart_items):
        if item['product_id'] == product_id:
            del cart_items[index]
            break
    session['cart'] = cart_items
    session.modified = True
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("DELETE FROM ShoppingCarts WHERE prod_id = %s", (product_id,))
            cursor.execute("""
                UPDATE products SET available_copies = available_copies + 1 WHERE product_id = %s
            """, (product_id,))
            conn.commit()
        flash('Product removed from cart.', 'success')
        return redirect(url_for('cart.cart'))
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    try:
        if 'cart' not in session or not session['cart']:
            flash('Your cart is empty!', 'warning')
            return redirect(url_for('cart.cart'))

        cart_items = session.get('cart', [])
        total_cost = sum(float(item['cost']) for item in cart_items)

        if request.method == 'POST':
            address = request.form.get('address')
            payment_method = request.form.get('payment_method')
            user_id = session.get('user_id')
            shopping_cart_id = session.get('shopping_cart_id')
            seller_id = cart_items[-1]['seller_id'] if cart_items else None

            data_access.create_order(user_id, address, payment_method, shopping_cart_id, seller_id, total_cost)

            session.pop('cart', None)
            session.modified = True
            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('products.index'))

        return render_template('cart/checkout.html', cart_items=cart_items, total_cost=total_cost)
    except Exception as err:
        return f"Database error: {err}", 500
