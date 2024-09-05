from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
import data_access
from data_access import get_db_connection


app = Flask(__name__)
app.secret_key = '135798642.A'

@app.route('/api/entities', methods=['GET', 'POST'])
def entities():
    if request.method == 'GET':
        return jsonify(data_access.get_entities())
    elif request.method == 'POST':
        data = request.get_json()
        new_entity = data_access.create_entity(data)
        return jsonify(new_entity), 201

@app.route('/api/entities/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def entity(id):
    if request.method == 'GET':
        entity = data_access.get_entity(id)
        if entity:
            return jsonify(entity)
        else:
            return jsonify({'error': 'Entity not found'}), 404
    elif request.method == 'PUT':
        data = request.get_json()
        updated_entity = data_access.update_entity(id, data)
        if updated_entity:
            return jsonify(updated_entity)
        else:
            return jsonify({'error': 'Entity not found'}), 404
    elif request.method == 'DELETE':
        success = data_access.delete_entity(id)
        if success:
            return '', 204
        else:
            return jsonify({'error': 'Entity not found'}), 404

@app.route('/')
def index():
    """Zeigt die Startseite an."""
    user_id = session.get('user_id')
    print(f"User ID from session: {user_id}")  # Debugging-Ausgabe

    try:
        # Abrufen der Kategorien
        results = data_access.get_categories()
        products = data_access.get_products()

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
        
        return render_template('product_list.html', products=products, user_id=user_id, categories=categories)
    except Exception as err:
        return f"Database error: {err}", 500

@app.route('/Seller_shop')
def seller_shop():
    seller_id = request.args.get('seller_id')
    if not seller_id:
        return "Seller ID is required", 400

    try:
        with data_access.get_db_connection() as connection:
            seller = data_access.get_seller_by_id(connection, seller_id)
            if not seller:
                return "Seller not found", 404
            products = data_access.get_products_by_seller_id(connection, seller_id)
        return render_template('seller_shop.html', seller=seller, products=products)
    except Exception as e:
        return f"Database error: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Behandelt die Anmeldung der Benutzer."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            user = data_access.get_user_by_username(username)

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                return redirect(url_for('index'))
            else:
                return "Invalid username or password", 401
        except Exception as err:
            return f"Database error: {err}", 500

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Behandelt die Registrierung neuer Benutzer."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        is_seller = 'is_seller' in request.form #Prüft, ob Kästchen für Verkäufer angeklickt ist
     
        try:
            shopname = request.form.get('shopname')
            website_url = request.form.get('website_url') 
                
            user_id = data_access.register_user(username, password, email, is_seller, shopname, website_url)
            if is_seller:
                shopname = request.form.get('shopname')
                website_url = request.form.get('website_url') 
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                            "INSERT INTO Sellers (seller_id, shopname, website_url) VALUES (%s, %s, %s)",
                            (user_id, shopname, website_url)
                        )
                conn.commit()
                
            session['user_id'] = user_id
            return redirect(url_for('login'))
        except Exception as err:
            return f"Database error: {err}", 500

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Behandelt das Logout der Benutzer und leitet zur Startseite weiter."""
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/profile/<int:user_id>', methods=['POST', 'GET'])
def user_profile(user_id):
    try:
        with get_db_connection() as conn:
            user = data_access.get_user_by_id(user_id)
            if not user:
                return "User not found", 404

            seller = data_access.get_seller_by_id(user_id)

            if request.method == 'POST' and 'is_seller' in request.form and not seller:
                shopname = request.form.get('shopname')
                data_access.insert_seller(user_id, shopname)
                flash('You have been registered as a seller!', 'success')
                return redirect(url_for('user_profile', user_id=user_id))
        
        session['user_id'] = user_id 
        return render_template('user_profile.html', user=user, seller=seller)
    except Exception as e:
        return f"Database error: {str(e)}", 500
    
    
@app.route('/update_user/<int:user_id>', methods=['POST', 'GET'])
def update_profile(user_id):
    new_username = request.form.get('username')
    new_email = request.form.get('email')

    try:
        data_access.update_user_profile(user_id, new_username, new_email)
        flash('Your profile has been updated successfully', 'success')
        return redirect(url_for('user_profile', user_id=user_id))
    except Exception as e:
        flash(f"Database error: {str(e)}", 'error')
        return redirect(url_for('user_profile', user_id=user_id))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if query:
        try:
            with get_db_connection() as connection:
                products = data_access.search_products(connection, query)
                return render_template('search_results.html', query=query, products=products)
        except Exception as e:
            return f"Database error: {str(e)}", 500
    else:
        return render_template('search_results.html', query=query, products=[])
      
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
        # Kategorien abrufen
        categories = data_access.get_categories()

        if category_id:
            # Alle Unterkategorien der ausgewählten Kategorie finden
            subcategory_ids = [category_id]
            subcategories = data_access.get_subcategories(category_id)

            # IDs der Unterkategorien sammeln
            while subcategories:
                new_subcategories = []
                for sub in subcategories:
                    subcategory_ids.append(sub['c_id'])
                    new_subcategories.extend(data_access.get_subcategories(sub['c_id']))
                subcategories = new_subcategories

            # Produkte aus den Kategorien und Unterkategorien abrufen
            products = data_access.get_products_by_category(subcategory_ids, order_by)
        else:
            products = data_access.get_all_products(order_by)

        return render_template('product_list.html', products=products, categories=categories, sort_by=sort_by, category_id=category_id)
    except Exception as err:
        return f"Database error: {err}", 500

@app.route('/buyer_statistics/<int:user_id>', methods=['GET'])
def buyer_statistics(user_id):
    try:
        with get_db_connection() as conn:
            # Abrufen der Benutzerinformationen des Verkäufers
            user = data_access.get_user_by_id(user_id)
            if not user:
                return "User not found", 404

            # Käuferstatistiken abrufen
            statistics = data_access.get_buyer_statistics(user_id)
            if not statistics:
                return "No statistics found", 404

            # Rendern der Käuferstatistik-Vorlage mit den Benutzer- und Statistikdaten
            return render_template('buyer_statistics.html', user=user, statistics=statistics)

    except Exception as e:
        return f"Database error: {str(e)}", 500

    
@app.route('/subscribe/<int:seller_id>/<int:product_id>', methods=['POST'])
def subscribe_to_seller(seller_id, product_id):
    """Erlaubt es einem Benutzer, sich bei einem Verkäufer anzumelden."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    try:
        if data_access.get_subscribe_to_seller(user_id, seller_id):
            flash('Successfully subscribed to the seller!', 'success')
        else:
            flash('You are already subscribed to this seller!', 'info')
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')

    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/order')
def order():
    user_id = session.get('user_id')  # Die ID des aktuell angemeldeten Benutzers aus der Session abrufen
    if not user_id:
        return redirect(url_for('login'))  # Wenn der Benutzer nicht eingeloggt ist, zur Login-Seite weiterleiten
    
    try:
        orders = data_access.get_orders_by_user_id(user_id)  # Bestellungen des Benutzers abrufen
        return render_template('order.html', orders=orders)
    except Exception as err:
        return f"Database error: {err}", 500

@app.route('/seller_orders')
def seller_orders():
    user_id = session.get('user_id')  # Die ID des aktuell angemeldeten Verkäufers aus der Session abrufen
    try:
        products = data_access.get_products_by_seller_id(user_id)  # Produkte des Verkäufers abrufen
        return render_template('seller_orders.html', products=products)
    except Exception as err:
        return f"Database error: {err}", 500

@app.route('/update_products', methods=['POST', 'GET'])
def update_products():
    user_id = session.get('user_id')
    try:
        products = data_access.get_products_by_seller_id_for_update(user_id)  # Alle Produkte des Verkäufers abrufen
        for product in products:
            product_id = product[0]
            # Neue Werte aus dem Formular abrufen
            new_cost = request.form.get(f'cost_{product_id}')
            new_copies = request.form.get(f'copies_{product_id}')
            new_info = request.form.get(f'info_{product_id}')

            # Update-Anweisung ausführen
            data_access.update_product(product_id, user_id, new_cost, new_copies, new_info)

        return redirect(url_for('seller_orders'))
    except Exception as err:
        return f"Database error: {err}", 500

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Zeigt die Detailseite eines Produkts an, einschließlich Bewertungen."""
    user_id = session.get('user_id')
    try:
        product = data_access.get_product_details(product_id)  # Produktdetails abrufen

        if not product:
            return "Product not found", 404

        reviews = data_access.get_product_reviews(product_id)  # Bewertungen abrufen

        product_in_wishlist = False
        if user_id:
            product_in_wishlist = data_access.is_product_in_wishlist(user_id, product_id)  # Wunschlistenstatus überprüfen

        return render_template('product_detail.html', product=product, reviews=reviews, user_id=user_id, product_in_wishlist=product_in_wishlist)
    except Exception as err:
        return f"Database error: {err}", 500


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

        # Benachrichtigung an alle Abonnenten senden
        cursor.execute("""
            SELECT user_id FROM Subscriptions
            WHERE seller_id = %s
        """, (user_id,))
        subscribers = cursor.fetchall()
    

        for subscriber in subscribers:
            cursor.execute("""
                INSERT INTO Messaging (message, sender_id, receiver_id)
                VALUES (%s, %s, %s)
            """, (f"New product '{name}' added by seller {seller['shopname']}. Check it out!", user_id, subscriber['user_id']))
            conn.commit()

        flash('Product added and subscribers notified!', 'success')
        
        return redirect(url_for('user_profile', user_id=user_id))
    except Exception as err:
        return f"Database error: {err}", 500
    finally:
        cursor.close()
        conn.close()

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

                if not product:
                    flash('Product not found!', 'error')
                    return redirect(url_for('index'))
                
                
                if product:
                # Überprüfen, ob genug Kopien verfügbar sind
                    if product['available_copies'] <= 0:
                        flash('Product is out of stock!', 'warning')
                        return redirect(url_for('product_detail', product_id=product_id))
                    # Überprüfen, ob der Benutzer der Verkäufer des Produkts ist
                    if product['seller_id'] == session.get('user_id'):
                        flash('You cannot add your own product to the cart!', 'warning')
                        return redirect(url_for('product_detail', product_id=product_id))

                    # Check if the cart is in the session
                    if 'cart' not in session:
                        session['cart'] = []

                    # Add the product to the cart
                    session['cart'].append(product)
                    session.modified = True

                    cursor.execute("""
                        INSERT INTO ShoppingCarts (user_id, prod_id)
                        VALUES (%s, %s)
                    """, (session.get('user_id'), product_id,))
                    conn.commit()

                    # Update the available copies in the database
                    cursor.execute("""
                        UPDATE products
                        SET available_copies = available_copies - 1
                        WHERE product_id = %s
                    """, (product_id,))
                    conn.commit()

                return redirect(url_for('cart'))  # Redirect to the cart page
            
    except Exception as err:
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
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    DELETE FROM ShoppingCarts WHERE prod_id = %s
                """, (product_id,))
                conn.commit()
                # Update the available copies in the database
                cursor.execute("""
                    UPDATE products
                    SET available_copies = available_copies + 1
                    WHERE product_id = %s
                """, (product_id,))
                conn.commit()

                flash('Product removed from cart.', 'success')
                return redirect(url_for('cart'))
            
    except Exception as err:
        return f"Database error: {err}", 500

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Handles the checkout process."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                if 'cart' not in session or not session['cart']:
                    flash('Your cart is empty!', 'warning')
                    return redirect(url_for('cart'))

                cart_items = session.get('cart', [])
                total_cost = sum(float(item['cost']) for item in cart_items)

                if request.method == 'POST':
                    address = request.form.get('address')
                    payment_method = request.form.get('payment_method')

                    user_id = session.get('user_id')
                    shopping_cart_id = session.get('shopping_cart_id')

                    cursor = conn.cursor()
                    cursor.execute("SELECT pm_id FROM PaymentMethods WHERE pm_name = %s", (payment_method,))
                    payment_id = cursor.fetchone()
                    
                    for item in cart_items:
                        seller_id = item['seller_id']

                    cursor.execute("""
                        INSERT INTO Orders (delivery_address, payment_id, shopping_cart_id, user_id, status, seller_id, total_amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (address, payment_id, shopping_cart_id, user_id, 'Processing', seller_id, total_cost))
                    
                    conn.commit()

                    # Reset the cart
                    session.pop('cart', None)
                    session.modified = True

                    # Send order confirmation
                    flash('Your order has been placed successfully!', 'success')
                    return redirect(url_for('index'))

                return render_template('checkout.html', cart_items=cart_items, total_cost=total_cost)
            
    except Exception as err:
        return f"Database error: {err}", 500    

@app.route('/add_review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Leitet nicht angemeldete Benutzer zur Login-Seite weiter
    
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user_id']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Überprüfen, ob der Benutzer der Verkäufer des Produkts ist
                cursor.execute("""
                    SELECT seller_id FROM products WHERE product_id = %s
                """, (product_id,))
                product = cursor.fetchone()
                
                if product and product['seller_id'] == user_id:
                    flash('You cannot review your own product!', 'warning')
                    return redirect(url_for('product_detail', product_id=product_id))
                
                cursor.execute("""
                    INSERT INTO Reviews (rating, product_id, reviewer, comment)
                    VALUES (%s, %s, %s, %s)
                """, (rating, product_id, user_id, comment))
                conn.commit()
                return redirect(url_for('product_detail', product_id=product_id))
    except Exception as err:
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
    except Exception as err:
        return f"Database error: {err}", 500


@app.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Überprüfen, ob der Benutzer der Verkäufer des Produkts ist
                cursor.execute("""
                    SELECT seller_id FROM products WHERE product_id = %s
                """, (product_id,))
                product = cursor.fetchone()
                
                if product and product['seller_id'] == user_id:
                    flash('You cannot add your own product to your wishlist!', 'warning')
                    return redirect(url_for('product_detail', product_id=product_id))
                
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
    except Exception as err:
        return f"Database error: {err}", 500


@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        wishlist_items = data_access.get_wishlist(user_id)  # Wunschliste abrufen
        
        return render_template('wishlist.html', wishlist_items=wishlist_items)
    except Exception as err:
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
    except Exception as err:
        return f"Database error: {err}", 500


@app.route('/messages')
def messages():
    """Zeigt eine Liste der Verkäufer an, mit denen der Benutzer Nachrichten ausgetauscht hat."""
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Leitet nicht angemeldete Benutzer zur Login-Seite weiter

    user_id = session['user_id']

    try:
        sellers = data_access.get_sellers_with_messages(user_id)  # Verkäufer abrufen

        return render_template('messages_overview.html', sellers=sellers)

    except Exception as err:
        return f"Database error: {err}", 500



@app.route('/messages/<int:seller_id>')
def view_chat(seller_id):
    """Zeigt den Chatverlauf mit einem bestimmten Verkäufer an."""
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Leitet nicht angemeldete Benutzer zur Login-Seite weiter

    user_id = session['user_id']

    try:
        messages = data_access.get_chat_messages(user_id, seller_id)  # Alle Nachrichten abrufen

        # Nachrichten formatieren
        chat = {
            'seller_id': seller_id,
            'seller_name': messages[0]['seller_name'] if messages else 'Unknown',
            'messages': [
                {
                    'content': message['message'],
                    'timestamp': message['sending_date'],
                    'sender': 'user' if message['sender_id'] == user_id else 'seller'
                }
                for message in messages
            ]
        }

        return render_template('chat.html', chat=chat)

    except Exception as err:
        return f"Database error: {err}", 500


@app.route('/messages/send/<int:seller_id>', methods=['POST'])
def send_message(seller_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Leitet nicht angemeldete Benutzer zur Login-Seite weiter

    content = request.form.get('content')
    user_id = session['user_id']

    if content:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO Messaging (message, sender_id, receiver_id)
                        VALUES (%s, %s, %s)
                    """, (content, user_id, seller_id))
                    conn.commit()
            flash('Message sent successfully!', 'success')
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    else:
        flash('Message content cannot be empty!', 'danger')

    return redirect(url_for('view_chat', seller_id=seller_id))

@app.route('/messages/start_chat', methods=['POST'])
def start_chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    receiver_name = request.form.get('receiver_name')
    sender_id = session['user_id']

    if receiver_name:
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    # Benutzer-ID basierend auf dem Benutzernamen abrufen
                    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (receiver_name,))
                    receiver = cursor.fetchone()

                    if not receiver:
                        flash('User not found.', 'danger')
                        return redirect(url_for('messages_overview'))

                    receiver_id = receiver['user_id']

                    # Prüfen, ob bereits ein Chat existiert
                    cursor.execute("""
                        SELECT * FROM Messaging
                        WHERE (sender_id = %s AND receiver_id = %s)
                        OR (sender_id = %s AND receiver_id = %s)
                    """, (sender_id, receiver_id, receiver_id, sender_id))
                    chat_exists = cursor.fetchone()

                    if chat_exists:
                        flash('Chat already exists!', 'warning')
                    else:
                        # Neuen Chat beginnen, indem eine erste Nachricht gesendet wird
                        cursor.execute("""
                            INSERT INTO Messaging (message, sender_id, receiver_id)
                            VALUES (%s, %s, %s)
                        """, ('', sender_id, receiver_id))
                        conn.commit()
                        flash('New chat started successfully!', 'success')

            return redirect(url_for('messages'))

        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    else:
        flash('Please enter a valid username.', 'danger')

    return redirect(url_for('messages_'))

@app.route('/new_products')
def new_products():
    user_id = session.get('user_id')  # Die ID des aktuell angemeldeten Benutzers abrufen

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Abonnierte Verkäufer ermitteln
        cursor.execute("""
            SELECT seller_id FROM Subscriptions
            WHERE user_id = %s
        """, (user_id,))
        subscribed_sellers = cursor.fetchall()

        if not subscribed_sellers:
            return "You are not subscribed to any sellers.", 404

        seller_ids = [seller['seller_id'] for seller in subscribed_sellers]

        # Neue Produkte von den abonnierten Verkäufern abrufen, zusammen mit den Shopnamen und Bildquellen
        cursor.execute("""
            SELECT p.name, p.cost, p.available_copies, p.information, s.shopname, pic.source
            FROM Products p
            JOIN Sellers s ON p.seller_id = s.seller_id
            JOIN Pictures pic ON p.picture_id = pic.pic_id
            WHERE p.seller_id IN (%s)
            ORDER BY p.product_id DESC
        """ % ','.join(['%s'] * len(seller_ids)), tuple(seller_ids))
        new_products = cursor.fetchall()

        return render_template('new_products.html', products=new_products)
    
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)