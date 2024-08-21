from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '135798642.A'  # Stelle sicher, dass dies gesetzt ist


# Konfiguration für die Verbindung zur MariaDB
db_config = {
    'user': 'aaron',
    'password': '135798642.A',
    'host': 'localhost',
    'database': 'onlineshop',
    'raise_on_warnings': True
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/')
def index():
    user_id = session.get('user_id')  # Holen des user_id aus der Session
    print(f"User ID from session: {user_id}")  # Debugging-Ausgabe
    return render_template('index.html', user_id=user_id)

@app.route('/products')
def product_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return render_template('product_list.html', products=products)
    except mysql.connector.Error as err:
        # Log or handle database error
        print(f"Database error: {err}")
        return "Database error", 500
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        return render_template('product_detail.html', product=product)
    finally:
        cursor.close()
        conn.close()

@app.route('/profile/<int:user_id>')
def user_profile(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        return render_template('user_profile.html', user=user)
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                return redirect(url_for('index'))
            else:
                return "Invalid username or password", 401
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            return redirect(url_for('login'))
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/cart')
def cart():
    # Placeholder for cart functionality
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Placeholder for checkout functionality
        return redirect(url_for('index'))

    return render_template('checkout.html')

if __name__ == "__main__":
    app.run(debug=True)
