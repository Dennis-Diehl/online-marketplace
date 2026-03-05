from flask import render_template, request, redirect, url_for, session, flash
from app import data_access
from app.db import get_db_connection
from app.utils import login_required
from . import bp


@bp.route('/wishlist')
@login_required
def wishlist():
    user_id = session['user_id']
    try:
        wishlist_items = data_access.get_wishlist(user_id)
        return render_template('wishlist/wishlist.html', wishlist_items=wishlist_items)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    user_id = session['user_id']
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT seller_id FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if product and product['seller_id'] == user_id:
                flash('You cannot add your own product to your wishlist!', 'warning')
                return redirect(url_for('products.product_detail', product_id=product_id))
            cursor.execute("SELECT * FROM Wishlist WHERE user_id = %s AND product_id = %s", (user_id, product_id))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO Wishlist (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
                conn.commit()
                flash('Product added to your wishlist!', 'success')
            else:
                flash('Product is already in your wishlist!', 'info')
        return redirect(url_for('products.product_detail', product_id=product_id))
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    user_id = session['user_id']
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Wishlist WHERE user_id = %s AND product_id = %s", (user_id, product_id))
            conn.commit()
        flash('Product removed from your wishlist.', 'success')
        return redirect(url_for('products.product_detail', product_id=product_id))
    except Exception as err:
        return f"Database error: {err}", 500
