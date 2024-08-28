from flask import Flask, flash, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.secret_key = '135798642.A'  # Stelle sicher, dass dies gesetzt ist

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
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    """Zeigt die Startseite an."""
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")  # Debugging-Ausgabe

    try:
        # Abrufen der Kategorien
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT c1.c_id AS category_id, c1.name AS category_name, c2.c_id AS subcategory_id, c2.name AS subcategory_name
                    FROM Category c1
                    LEFT JOIN Category c2 ON c2.superiorc_id = c1.c_id
                    WHERE c1.superiorc_id IS NULL
                """)
                results = cursor.fetchall()

                categories = {}
                for row in results:
                    cat_id = row['category_id']
                    if cat_id not in categories:
                        categories[cat_id] = {
                            'name': row['category_name'],
                            'subcategories': []
                        }
                    if row['subcategory_id']:
                        categories[cat_id]['subcategories'].append({
                            'id': row['subcategory_id'],
                            'name': row['subcategory_name']
                        })

        # Abrufen der Produkte
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM products p JOIN Pictures pi ON p.picture_id = pi.pic_id")
                products = cursor.fetchall()
                return render_template('product_list.html', products=products, user_id=user_id, categories=categories)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

    

@app.route('/products')
def product_list():
    """Zeigt eine Liste von Produkten an und ermöglicht die Sortierung sowie Filterung nach Kategorien."""
    sort_by = request.args.get('sort_by', 'name_asc')  # Standardmäßig nach Namen aufsteigend sortieren
    category_id = request.args.get('category_id')  # Kategorie-Filter

    sort_options = {
        'price_asc': 'p.cost ASC',
        'price_desc': 'p.cost DESC',
        'name_asc': 'p.name ASC',
        'name_desc': 'p.name DESC'
    }

    order_by = sort_options.get(sort_by, 'p.name ASC')  # Standard-Sortierung

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Kategorien für das Dropdown-Menü abrufen
                cursor.execute("""
                    SELECT c1.c_id AS category_id, c1.name AS category_name, c2.c_id AS subcategory_id, c2.name AS subcategory_name
                    FROM Category c1
                    LEFT JOIN Category c2 ON c2.superiorc_id = c1.c_id
                    WHERE c1.superiorc_id IS NULL
                """)
                results = cursor.fetchall()
                
                categories = {}
                for row in results:
                    cat_id = row['category_id']
                    if cat_id not in categories:
                        categories[cat_id] = {
                            'name': row['category_name'],
                            'subcategories': []
                        }
                    if row['subcategory_id']:
                        categories[cat_id]['subcategories'].append({
                            'id': row['subcategory_id'],
                            'name': row['subcategory_name']
                        })

                # Alle Unterkategorien der ausgewählten Kategorie finden
                if category_id:
                    # Erstellen einer Liste für die IDs der Kategorien
                    subcategory_ids = [category_id]

                    # Schritt 1: Alle direkten Unterkategorien der ausgewählten Kategorie finden
                    cursor.execute("""
                        SELECT c_id
                        FROM Category
                        WHERE superiorc_id = %s
                    """, (category_id,))
                    subcategories = cursor.fetchall()
                    
                    # IDs der Unterkategorien sammeln
                    while subcategories:
                        new_subcategories = []
                        for sub in subcategories:
                            subcategory_ids.append(sub['c_id'])
                            cursor.execute("""
                                SELECT c_id
                                FROM Category
                                WHERE superiorc_id = %s
                            """, (sub['c_id'],))
                            new_subcategories.extend(cursor.fetchall())
                        subcategories = new_subcategories
                    
                    # Produkte aus den Kategorien und Unterkategorien abrufen
                    query = """
                        SELECT p.*, pi.source 
                        FROM products p 
                        JOIN pictures pi ON p.picture_id = pi.pic_id 
                        WHERE p.category_id IN (%s)
                        ORDER BY %s
                    """ % (','.join(['%s'] * len(subcategory_ids)), order_by)
                    cursor.execute(query, tuple(subcategory_ids))
                else:
                    # Keine Kategorie ausgewählt, alle Produkte abrufen
                    cursor.execute("""
                        SELECT p.*, pi.source 
                        FROM products p 
                        JOIN pictures pi ON p.picture_id = pi.pic_id 
                        ORDER BY %s
                    """ % order_by)
                
                products = cursor.fetchall()

                return render_template('product_list.html', products=products, categories=categories, sort_by=sort_by, category_id=category_id)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Zeigt die Detailseite eines Produkts an, einschließlich Bewertungen."""
    user_id = session.get('user_id')
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Produktdetails abrufen
                cursor.execute("""
                    SELECT p.*, s.website_url, pi.source
                    FROM products p 
                    JOIN Sellers s ON p.seller_id = s.seller_id 
                    JOIN Pictures pi ON p.picture_id = pi.pic_id
                    WHERE p.product_id = %s
                """, (product_id,))
                product = cursor.fetchone()
                
                # Bewertungen abrufen
                cursor.execute("""
                    SELECT r.*, u.username
                    FROM Reviews r
                    JOIN Users u ON r.reviewer = u.user_id
                    WHERE r.product_id = %s
                    ORDER BY r.r_date DESC
                """, (product_id,))
                reviews = cursor.fetchall()

                product_in_wishlist = False
                if user_id:
                    # Überprüfen, ob das Produkt in der Wunschliste des Benutzers ist
                    cursor.execute("""
                        SELECT * FROM Wishlist
                        WHERE user_id = %s AND product_id = %s
                    """, (user_id, product_id))
                    product_in_wishlist = cursor.fetchone() is not None

                return render_template('product_detail.html', product=product, reviews=reviews, user_id=user_id, product_in_wishlist=product_in_wishlist)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500




@app.route('/profile/<int:user_id>', methods = ['POST', 'GET'])
def user_profile(user_id):
    """Zeigt das Profil eines Benutzers an."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()

                if user is None:
                    return "User not found", 404
                
                cursor.execute("SELECT * FROM Sellers WHERE seller_id = %s", (user_id,))
                seller = cursor.fetchone()
            
                if  request.method == 'POST' and 'is_seller' in request.form and not seller:
                    shopname = request.form.get('shopname')
                    cursor.execute(
                        "INSERT INTO Sellers (seller_id, shopname) VALUES (%s, %s)",
                        (user_id, shopname)
                    )
                    conn.commit()
                    flash('You have been registered as a seller!', 'success')
                    return redirect(url_for('user_profile'), user_id = user_id)
                
            conn.commit()
        session['user_id'] = user_id 
        return render_template('user_profile.html', user=user, seller = seller)
    
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Behandelt die Anmeldung der Benutzer."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                    user = cursor.fetchone()

                    if user and check_password_hash(user['password'], password):
                        session['user_id'] = user['user_id']
                        return redirect(url_for('index'))
                    else:
                        return "Invalid username or password", 401
        except mysql.connector.Error as err:
            return f"Database error: {err}", 500

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Behandelt die Registrierung neuer Benutzer."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        hashed_password = generate_password_hash(password)
        is_seller = 'is_seller' in request.form #Prüft, ob Kästchen für Verkäufer angeklickt ist

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    today = str(date.today())
                    cursor.execute(
                        "INSERT INTO users (username, password, acc_creation_date, email) VALUES (%s, %s, %s, %s)",
                        (username, hashed_password, today, email)
                    )
                    conn.commit()
                    user_id = cursor.lastrowid  # Holen der ID des neu erstellten Benutzers

                    if is_seller:
                        shopname = request.form.get('shopname')
                        website_url = request.form.get('website_url')
                        cursor.execute(
                            "INSERT INTO Sellers (seller_id, shopname, website_url) VALUES (%s, %s, %s)",
                            (user_id, shopname, website_url)
                        )
                        conn.commit()
                    session['user_id'] = user_id  # Setzt die Session-ID für den Benutzer
                    return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Database error: {err}", 500

    return render_template('register.html')

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart_items=cart_items)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
                product = cursor.fetchone()
                
                if product:
                    # Check if the cart is in the session
                    if 'cart' not in session:
                        session['cart'] = []

                    # Add the product to the cart
                    session['cart'].append(product)
                    session.modified = True

                return redirect(url_for('cart'))  # Redirect to the cart page
            
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    for index, item in enumerate(cart):
        if item['product_id'] == product_id:
            del cart[index]
            break 

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart'))



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Handles the checkout process."""
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))

    cart_items = session.get('cart', [])
    total_cost = sum(float(item['cost']) for item in cart_items)

    if request.method == 'POST':
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')

        # Here, you would typically handle payment processing and store the order details
        # For simplicity, let's assume the order is successfully placed

        # Reset the cart
        session.pop('cart', None)
        session.modified = True

        # Send order confirmation
        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('checkout.html', cart_items=cart_items, total_cost=total_cost)



@app.route('/logout')
def logout():
    """Behandelt das Logout der Benutzer und leitet zur Startseite weiter."""
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/add_product/<int:user_id>', methods=['POST'])
def add_product(user_id):
    name = request.form.get('name')
    cost = request.form.get('cost')
    available_copies = request.form.get('available_copies')
    category_name = request.form.get('category_name')  # Kategorienaame aus dem Formular holen
    information = request.form.get('information')
    pict_url = request.form.get('picture_url')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Überprüfen, ob der Benutzer ein Verkäufer ist
        cursor.execute("SELECT * FROM Sellers WHERE seller_id = %s", (user_id,))
        seller = cursor.fetchone()
        
        if not seller:
            shopname = f"Shop von {name}"  # Standard-Name für den Shop
            cursor.execute(
                "INSERT INTO Sellers (seller_id, shopname) VALUES (%s, %s)",
                (user_id, shopname)
            )
            conn.commit()

        # Neues Produktbild hinzufügen
        cursor.execute("""
                       INSERT INTO Pictures (source)
                       VALUES (%s)
                       """,(pict_url,))
        conn.commit()


        # Ermitteln der Kategorie-ID basierend auf dem Kategoriernamen
        cursor.execute("SELECT c_id FROM Category WHERE name = %s", (category_name,))
        category = cursor.fetchone()
        

        cursor.execute("SELECT pic_id FROM Pictures ORDER BY pic_id DESC LIMIT 1")
        pict = cursor.fetchone()

        if pict:
            picture_id = pict['pic_id']
        else:
            return "Picture not found", 404
        
        if category:
            category_id = category['c_id']
        else:
            return "Category not found", 404

        # Hinzufügen des Produkts zur Datenbank
        cursor.execute("""
            INSERT INTO Products (name, cost, available_copies, category_id, information, picture_id, seller_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, cost, available_copies, category_id, information, picture_id, user_id))
        conn.commit()
        
        return redirect(url_for('user_profile', user_id=user_id))
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    finally:
        cursor.close()
        conn.close()


@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if query:
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    # Suche nach Produkten, die den Suchbegriff im Namen enthalten
                    cursor.execute("""
                        SELECT * FROM products p 
                        JOIN pictures pi ON p.picture_id = pi.pic_id 
                        WHERE p.name LIKE %s
                    """, ('%' + query + '%',))
                    products = cursor.fetchall()
                    return render_template('search_results.html', query=query, products=products)
        except mysql.connector.Error as err:
            return f"Database error: {err}", 500
    else:
        # Falls kein Suchbegriff eingegeben wurde, leere Ergebnisse anzeigen
        return render_template('search_results.html', query=query, products=[])


@app.route('/add_review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    """Ermöglicht es angemeldeten Benutzern, eine Bewertung für ein Produkt hinzuzufügen."""
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Leitet nicht angemeldete Benutzer zur Login-Seite weiter
    
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user_id']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Reviews (rating, product_id, reviewer, comment)
                    VALUES (%s, %s, %s, %s)
                """, (rating, product_id, user_id, comment))
                conn.commit()
                return redirect(url_for('product_detail', product_id=product_id))
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    
@app.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    """Ermöglicht es Benutzern, ihre eigene Bewertung zu löschen."""
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Leitet nicht angemeldete Benutzer zur Login-Seite weiter

    user_id = session['user_id']

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Überprüfen, ob der Benutzer die Bewertung verfasst hat
                cursor.execute("""
                    SELECT reviewer FROM Reviews WHERE r_id = %s
                """, (review_id,))
                review = cursor.fetchone()

                if review and review['reviewer'] == user_id:
                    cursor.execute("""
                        DELETE FROM Reviews WHERE r_id = %s
                    """, (review_id,))
                    conn.commit()

            # Redirect zur Detailseite des Produkts
            product_id = request.form.get('product_id')
            return redirect(url_for('product_detail', product_id=product_id))
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

@app.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Überprüfen, ob das Produkt bereits in der Wishlist ist
                cursor.execute("SELECT * FROM Wishlist WHERE user_id = %s AND product_id = %s", (user_id, product_id))
                existing_wishlist_item = cursor.fetchone()
                
                if not existing_wishlist_item:
                    cursor.execute("INSERT INTO Wishlist (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
                    conn.commit()
                    flash('Product added to your wishlist!', 'success')
                else:
                    flash('Product is already in your wishlist!', 'info')
                
                return redirect(url_for('product_detail', product_id=product_id))
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500


@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT p.*, pi.source 
                    FROM Wishlist w
                    JOIN products p ON w.product_id = p.product_id
                    JOIN pictures pi ON p.picture_id = pi.pic_id
                    WHERE w.user_id = %s
                """, (user_id,))
                wishlist_items = cursor.fetchall()
                
                return render_template('wishlist.html', wishlist_items=wishlist_items)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500


@app.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM Wishlist WHERE user_id = %s AND product_id = %s", (user_id, product_id))
                conn.commit()
                flash('Product removed from your wishlist.', 'success')
                return redirect(url_for('product_detail', product_id = product_id))
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500



if __name__ == "__main__":
    app.run(debug=True)

