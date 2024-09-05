import mysql.connector
from mysql.connector import Error
from flask import g
from datetime import date
from werkzeug.security import generate_password_hash

# Konfiguration für die Verbindung zur MariaDB
db_config = {
    'user': 'dennis',
    'password': 'füller',
    'host': 'localhost',
    'database': 'marktplatz',
    'raise_on_warnings': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

def get_db_connection():
    """Stellt eine Verbindung zur Datenbank her."""
    if 'db' not in g:
        g.db = mysql.connector.connect(**db_config)
    return g.db

def close_db_connection(exception=None):
    """Schließt die Datenbankverbindung."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Abrufen der Kategorien
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
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()

def get_subcategories(category_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c_id
            FROM Category
            WHERE superiorc_id = %s
        """, (category_id,))
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()

def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM products p JOIN Pictures pi ON p.picture_id = pi.pic_id")
        products = cursor.fetchall()
        return products
    finally:
        cursor.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
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
        user_id = cursor.lastrowid  # Holen der ID des neu erstellten Benutzers
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
    """Holt die Verkäuferdaten für eine gegebene Verkäufer-ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Sellers WHERE seller_id = %s", (seller_id,))
        return cursor.fetchone()
    finally:
        cursor.close()

def get_products_by_seller_id(seller_id):
    """Holt die Produkte eines Verkäufers anhand der Verkäufer-ID."""
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
    """Holt die Benutzerdaten für eine gegebene Benutzer-ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()

def insert_seller(user_id, shopname):
    """Fügt einen neuen Verkäufer in die Datenbank ein."""
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
    """Aktualisiert die Benutzerinformationen."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if new_username:
            cursor.execute("""
                UPDATE Users SET username = %s WHERE user_id = %s
            """, (new_username, user_id))
        if new_email:
            cursor.execute("""
                UPDATE Users SET email = %s WHERE user_id = %s
            """, (new_email, user_id))
        conn.commit()
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()

def search_products(query):
    """Sucht nach Produkten basierend auf einem Suchbegriff."""
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
    """Holt alle verfügbaren Produkte sortiert nach den angegebenen Parametern."""
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
    """Holt alle Produkte, die zu bestimmten Unterkategorien gehören."""
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
    query = """
    SELECT u.username AS buyer_username, 
           COUNT(o.order_id) AS num_orders, 
           SUM(o.total_amount) AS total_amount
    FROM Orders o
    JOIN Users u ON o.user_id = u.user_id
    WHERE o.seller_id = %s
    GROUP BY u.username;
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (seller_id,))
        return cursor.fetchall()



def get_subscribe_to_seller(user_id, seller_id):
    """Fügt eine Subscription des Benutzers bei einem Verkäufer hinzu, wenn noch keine existiert."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Überprüfen, ob bereits eine Subscription existiert
        cursor.execute("""
            SELECT * FROM Subscriptions
            WHERE user_id = %s AND seller_id = %s
        """, (user_id, seller_id))
        existing_subscription = cursor.fetchone()

        if not existing_subscription:
            cursor.execute("""
                INSERT INTO Subscriptions (user_id, seller_id)
                VALUES (%s, %s)
            """, (user_id, seller_id))
            conn.commit()
            return True
        else:
            return False
    except Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()

def get_orders_by_user_id(user_id):
    """Holt alle Bestellungen eines Benutzers anhand der Benutzer-ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT order_id, delivery_address, payment_id, shopping_cart_id, status
            FROM Orders
            WHERE user_id = %s
        """, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()

def get_products_by_seller_id_for_update(seller_id):
    """Holt alle Produkte eines Verkäufers für die Aktualisierung."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT product_id FROM Products WHERE seller_id = %s", (seller_id,))
        return cursor.fetchall()
    finally:
        cursor.close()

def update_product(product_id, user_id, new_cost, new_copies, new_info):
    """Aktualisiert ein Produkt mit neuen Werten."""
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
    """Holt die Details eines Produkts einschließlich Verkäuferinformationen."""
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
    """Holt alle Bewertungen für ein bestimmtes Produkt."""
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
    """Überprüft, ob ein Produkt in der Wunschliste des Benutzers ist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM Wishlist
            WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))
        return cursor.fetchone() is not None
    finally:
        cursor.close()


def get_wishlist(user_id):
    """Holt alle Produkte aus der Wunschliste eines Benutzers."""
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
    """Holt die Verkäufer, mit denen der Benutzer Nachrichten ausgetauscht hat."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT DISTINCT 
                u.user_id AS seller_id, 
                u.username AS seller_name
            FROM 
                Messaging m
            JOIN 
                Users u ON u.user_id = m.sender_id OR u.user_id = m.receiver_id
            WHERE 
                (m.sender_id = %s OR m.receiver_id = %s) AND u.user_id != %s
        """, (user_id, user_id, user_id))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_chat_messages(user_id, seller_id):
    """Holt alle Nachrichten zwischen einem Benutzer und einem Verkäufer."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                m.m_id,
                m.sending_date,
                m.message,
                m.sender_id,
                u.username AS seller_name
            FROM 
                Messaging m
            JOIN 
                Users u ON m.sender_id = u.user_id
            WHERE 
                (m.sender_id = %s AND m.receiver_id = %s) OR
                (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY 
                m.sending_date ASC
        """, (user_id, seller_id, seller_id, user_id))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_entities():
    conn = get_db_connection()
    entities = conn.execute('SELECT * FROM entities').fetchall()
    conn.close()
    return [dict(row) for row in entities]

def get_entity(id):
    conn = get_db_connection()
    entity = conn.execute('SELECT * FROM entities WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(entity) if entity else None

def create_entity(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO entities (name, value) VALUES (?, ?)',
                   (data['name'], data['value']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {'id': new_id, **data}

def update_entity(id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE entities SET name = ?, value = ? WHERE id = ?',
                   (data['name'], data['value'], id))
    conn.commit()
    conn.close()
    if cursor.rowcount:
        return {'id': id, **data}
    else:
        return None

def delete_entity(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM entities WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

