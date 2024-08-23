from flask import Flask, render_template, request, redirect, url_for, session
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
    categories = get_categories()  # Holen der Kategorien
    return render_template('index.html', user_id=user_id, categories=categories)

@app.route('/products')
def product_list():
    """Zeigt eine Liste von Produkten an."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM products p JOIN Pictures pi ON p.picture_id = pi.pic_id")
                products = cursor.fetchall()
                return render_template('product_list.html', products=products)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Zeigt die Detailseite eines Produkts an."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM products p JOIN pictures pi ON p.picture_id = pi.pic_id WHERE product_id = %s", (product_id,))
                product = cursor.fetchone()
                return render_template('product_detail.html', product=product)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

@app.route('/profile/<int:user_id>')
def user_profile(user_id):
    """Zeigt das Profil eines Benutzers an."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user = cursor.fetchone()
                return render_template('user_profile.html', user=user)
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

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    today = str(date.today())
                    cursor.execute(
                        "INSERT INTO users (username, password, acc_creation_date, email) VALUES (%s, %s, %s, %s)",
                        (username, hashed_password, today, email)
                    )
                    conn.commit()
                    return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return f"Database error: {err}", 500

    return render_template('register.html')

@app.route('/cart')
def cart():
    """Zeigt den Warenkorb an."""
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Behandelt den Checkout-Prozess."""
    if request.method == 'POST':
        # Placeholder für Checkout-Funktionalität
        return redirect(url_for('index'))

    return render_template('checkout.html')

@app.route('/search')
def search():
    """Behandelt Suchanfragen."""
    query = request.args.get('query')
    c_id = request.args.get('category')
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                if c_id and c_id != 'all':
                    cursor.execute(
                        "SELECT * FROM products WHERE name LIKE %s AND c_id = %s",
                        (f"%{query}%", c_id)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM products WHERE name LIKE %s",
                        (f"%{query}%",)
                    )
                results = cursor.fetchall()
                return render_template('search_results.html', results=results)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500


@app.route('/logout')
def logout():
    """Behandelt das Logout der Benutzer und leitet zur Startseite weiter."""
    session.pop('user_id', None)
    return redirect(url_for('index'))

def get_categories():
    """Holt alle Kategorien aus der Datenbank und organisiert sie in einem hierarchischen Format."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM Category WHERE superiorc_id IS NULL")
                root_categories = cursor.fetchall()

                cursor.execute("SELECT * FROM Category WHERE superiorc_id IS NOT NULL")
                sub_categories = cursor.fetchall()

                subcategories_dict = {}
                for sub in sub_categories:
                    parent_id = sub['superiorc_id']
                    if parent_id not in subcategories_dict:
                        subcategories_dict[parent_id] = []
                    subcategories_dict[parent_id].append({
                        'id': sub['c_id'],
                        'name': sub['name']
                    })

                # Hinzufügen der Unterkategorien zu den Wurzelkategorien
                for cat in root_categories:
                    cat['subcategories'] = subcategories_dict.get(cat['c_id'], [])

                return root_categories

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []

@app.route('/add_product/<int:user_id>', methods=['POST'])
def add_product(user_id):
    name = request.form.get('name')
    cost = request.form.get('cost')
    available_copies = request.form.get('available_copies')
    category_id = request.form.get('category_id')
    information = request.form.get('information')
    picture_id = request.form.get('picture_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Products (name, cost, available_copies, category_id, information, picture_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, cost, available_copies, category_id, information, picture_id))
        conn.commit()
        return redirect(url_for('user_profile', user_id=user_id))
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
