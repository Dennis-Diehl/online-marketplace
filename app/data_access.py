from mysql.connector import Error
from datetime import date
from werkzeug.security import generate_password_hash
from .db import get_db_connection


def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT DISTINCT c1.c_id AS category_id, c1.name AS category_name, c2.c_id AS subcategory_id, c2.name AS subcategory_name
            FROM Category c1
            LEFT JOIN Category c2 ON c2.superiorc_id = c1.c_id
            WHERE c1.superiorc_id IS NULL
        """)
        return cursor.fetchall()
    finally:
        cursor.close()


def get_subcategories(category_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT c_id FROM Category WHERE superiorc_id = %s", (category_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM products p JOIN Pictures pi ON p.picture_id = pi.pic_id")
        return cursor.fetchall()
    finally:
        cursor.close()


def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    finally:
        cursor.close()


def register_user(username, password, email, is_seller, shopname=None, website_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    today = str(date.today())
    try:
        cursor.execute(
            "INSERT INTO users (username, password, acc_creation_date, email) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, today, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        if is_seller:
            cursor.execute(
                "INSERT INTO Sellers (seller_id, shopname, website_url) VALUES (%s, %s, %s)",
                (user_id, shopname, website_url)
            )
            conn.commit()
        return user_id
    finally:
        cursor.close()


def get_seller_by_id(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Sellers WHERE seller_id = %s", (seller_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def get_products_by_seller_id(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM Products p
            JOIN Pictures pi ON p.picture_id = pi.pic_id
            WHERE seller_id = %s
        """, (seller_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def insert_seller(user_id, shopname):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Sellers (seller_id, shopname) VALUES (%s, %s)",
            (user_id, shopname)
        )
        conn.commit()
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()


def update_user_profile(user_id, new_username=None, new_email=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if new_username:
            cursor.execute("UPDATE Users SET username = %s WHERE user_id = %s", (new_username, user_id))
        if new_email:
            cursor.execute("UPDATE Users SET email = %s WHERE user_id = %s", (new_email, user_id))
        conn.commit()
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()


def search_products(query):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM products p
            JOIN pictures pi ON p.picture_id = pi.pic_id
            WHERE p.name LIKE %s AND p.available_copies > 0
        """, ('%' + query + '%',))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_all_products(order_by):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.*, pi.source
            FROM products p
            JOIN pictures pi ON p.picture_id = pi.pic_id
            WHERE p.available_copies > 0
            ORDER BY %s
        """ % order_by)
        return cursor.fetchall()
    finally:
        cursor.close()


def get_products_by_category(subcategory_ids, order_by):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.*, pi.source
            FROM products p
            JOIN pictures pi ON p.picture_id = pi.pic_id
            WHERE p.category_id IN (%s) AND p.available_copies > 0
            ORDER BY %s
        """ % (','.join(['%s'] * len(subcategory_ids)), order_by)
        cursor.execute(query, tuple(subcategory_ids))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_buyer_statistics(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.username AS buyer_username,
                   COUNT(o.order_id) AS num_orders,
                   SUM(o.total_amount) AS total_amount
            FROM Orders o
            JOIN Users u ON o.user_id = u.user_id
            WHERE o.seller_id = %s
            GROUP BY u.username
        """, (seller_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_product_statistics(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.name AS product_name,
                   sci.quantity AS total_sold,
                   SUM(sci.quantity * p.cost) AS total_revenue
            FROM ShoppingCartItems sci
            JOIN Products p ON sci.product_id = p.product_id
            JOIN Orders o ON o.shopping_cart_id = sci.cart_id
            WHERE p.seller_id = %s
            GROUP BY p.name
        """, (seller_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_subscribe_to_seller(user_id, seller_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM Subscriptions WHERE user_id = %s AND seller_id = %s
        """, (user_id, seller_id))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute(
                "INSERT INTO Subscriptions (user_id, seller_id) VALUES (%s, %s)",
                (user_id, seller_id)
            )
            conn.commit()
            return True
        return False
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()


def get_orders_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT order_id, delivery_address, payment_id, shopping_cart_id, status
            FROM Orders WHERE user_id = %s
        """, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_products_by_seller_id_for_update(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT product_id FROM Products WHERE seller_id = %s", (seller_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def update_product(product_id, user_id, new_cost, new_copies, new_info):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Products
            SET cost = %s, available_copies = %s, information = %s
            WHERE product_id = %s AND seller_id = %s
        """, (new_cost, new_copies, new_info, product_id, user_id))
        conn.commit()
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()


def get_product_details(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.*, s.seller_id, s.shopname, s.website_url, pi.source
            FROM products p
            INNER JOIN Sellers s ON p.seller_id = s.seller_id
            INNER JOIN Pictures pi ON p.picture_id = pi.pic_id
            WHERE p.product_id = %s
        """, (product_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def get_product_reviews(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.*, u.username
            FROM Reviews r
            INNER JOIN Users u ON r.reviewer = u.user_id
            WHERE r.product_id = %s
            ORDER BY r.r_date DESC
        """, (product_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def is_product_in_wishlist(user_id, product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM Wishlist WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))
        return cursor.fetchone() is not None
    finally:
        cursor.close()


def get_wishlist(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.*, pi.source
            FROM Wishlist w
            JOIN products p ON w.product_id = p.product_id
            JOIN pictures pi ON p.picture_id = pi.pic_id
            WHERE w.user_id = %s
        """, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_sellers_with_messages(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT DISTINCT u.user_id AS seller_id, u.username AS seller_name
            FROM Messaging m
            JOIN Users u ON u.user_id = m.sender_id OR u.user_id = m.receiver_id
            WHERE (m.sender_id = %s OR m.receiver_id = %s) AND u.user_id != %s
        """, (user_id, user_id, user_id))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_chat_messages(user_id, seller_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT m.m_id, m.sending_date, m.message, m.sender_id, u.username AS seller_name
            FROM Messaging m
            JOIN Users u ON m.sender_id = u.user_id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.sending_date ASC
        """, (user_id, seller_id, seller_id, user_id))
        return cursor.fetchall()
    finally:
        cursor.close()


def create_order(user_id, delivery_address, payment_method, shopping_cart_id, seller_id, total):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT pm_id FROM PaymentMethods WHERE pm_name = %s", (payment_method,))
        payment_row = cursor.fetchone()
        payment_id = payment_row[0] if payment_row else None
        cursor.execute("""
            INSERT INTO Orders (delivery_address, payment_id, shopping_cart_id, user_id, status, seller_id, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (delivery_address, payment_id, shopping_cart_id, user_id, 'Processing', seller_id, total))
        conn.commit()
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()


def add_product_to_db(user_id, name, cost, available_copies, category_name, information, pict_url):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Sellers WHERE seller_id = %s", (user_id,))
        seller = cursor.fetchone()
        if not seller:
            shopname = f"Shop von {name}"
            cursor.execute(
                "INSERT INTO Sellers (seller_id, shopname) VALUES (%s, %s)",
                (user_id, shopname)
            )
            conn.commit()
            seller = {'shopname': shopname}

        cursor.execute("INSERT INTO Pictures (source) VALUES (%s)", (pict_url,))
        conn.commit()

        cursor.execute("SELECT c_id FROM Category WHERE name = %s", (category_name,))
        category = cursor.fetchone()
        if not category:
            raise ValueError("Category not found")

        cursor.execute("SELECT pic_id FROM Pictures ORDER BY pic_id DESC LIMIT 1")
        pict = cursor.fetchone()
        if not pict:
            raise ValueError("Picture not found")

        picture_id = pict['pic_id']
        category_id = category['c_id']

        cursor.execute("""
            INSERT INTO Products (name, cost, available_copies, category_id, information, picture_id, seller_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, cost, available_copies, category_id, information, picture_id, user_id))
        conn.commit()

        cursor.execute("SELECT user_id FROM Subscriptions WHERE seller_id = %s", (user_id,))
        subscribers = cursor.fetchall()
        for subscriber in subscribers:
            cursor.execute("""
                INSERT INTO Messaging (message, sender_id, receiver_id)
                VALUES (%s, %s, %s)
            """, (f"New product '{name}' added by seller {seller['shopname']}. Check it out!", user_id, subscriber['user_id']))
            conn.commit()
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()


def get_new_products_for_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT seller_id FROM Subscriptions WHERE user_id = %s", (user_id,))
        subscribed_sellers = cursor.fetchall()
        if not subscribed_sellers:
            return []
        seller_ids = [seller['seller_id'] for seller in subscribed_sellers]
        query = """
            SELECT p.name, p.cost, p.available_copies, p.information, s.shopname, pic.source
            FROM Products p
            JOIN Sellers s ON p.seller_id = s.seller_id
            JOIN Pictures pic ON p.picture_id = pic.pic_id
            WHERE p.seller_id IN (%s)
            ORDER BY p.product_id DESC
        """ % ','.join(['%s'] * len(seller_ids))
        cursor.execute(query, tuple(seller_ids))
        return cursor.fetchall()
    finally:
        cursor.close()
