from flask import jsonify, session
from app.db import get_db_connection
from . import bp


def _require_login():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    return None


@bp.route('/cart/<int:product_id>', methods=['POST'])
def api_add_to_cart(product_id):
    auth_error = _require_login()
    if auth_error:
        return auth_error
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if not product:
                return jsonify({"success": False, "error": "Product not found"}), 404
            if product['available_copies'] <= 0:
                return jsonify({"success": False, "error": "Product is out of stock"}), 409
            if product['seller_id'] == session['user_id']:
                return jsonify({"success": False, "error": "You cannot add your own product to the cart"}), 403
            if 'cart' not in session:
                session['cart'] = []
            session['cart'].append(product)
            session.modified = True
            cursor.execute(
                "INSERT INTO ShoppingCarts (user_id, prod_id) VALUES (%s, %s)",
                (session['user_id'], product_id)
            )
            cursor.execute(
                "UPDATE products SET available_copies = available_copies - 1 WHERE product_id = %s",
                (product_id,)
            )
            conn.commit()
        return jsonify({"success": True, "cart_count": len(session['cart'])})
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500


@bp.route('/cart/<int:product_id>', methods=['DELETE'])
def api_remove_from_cart(product_id):
    auth_error = _require_login()
    if auth_error:
        return auth_error
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
            cursor.execute(
                "UPDATE products SET available_copies = available_copies + 1 WHERE product_id = %s",
                (product_id,)
            )
            conn.commit()
        return jsonify({"success": True, "cart_count": len(session['cart'])})
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500


@bp.route('/wishlist/<int:product_id>', methods=['POST'])
def api_add_to_wishlist(product_id):
    auth_error = _require_login()
    if auth_error:
        return auth_error
    user_id = session['user_id']
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT seller_id FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if not product:
                return jsonify({"success": False, "error": "Product not found"}), 404
            if product['seller_id'] == user_id:
                return jsonify({"success": False, "error": "You cannot add your own product to your wishlist"}), 403
            cursor.execute(
                "SELECT * FROM Wishlist WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )
            if cursor.fetchone():
                return jsonify({"success": False, "error": "Product is already in your wishlist"}), 409
            cursor.execute(
                "INSERT INTO Wishlist (user_id, product_id) VALUES (%s, %s)",
                (user_id, product_id)
            )
            conn.commit()
        return jsonify({"success": True, "in_wishlist": True})
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500


@bp.route('/wishlist/<int:product_id>', methods=['DELETE'])
def api_remove_from_wishlist(product_id):
    auth_error = _require_login()
    if auth_error:
        return auth_error
    user_id = session['user_id']
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Wishlist WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )
            conn.commit()
        return jsonify({"success": True, "in_wishlist": False})
    except Exception as err:
        return jsonify({"success": False, "error": str(err)}), 500
