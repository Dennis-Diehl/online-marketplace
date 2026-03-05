from flask import render_template, request, redirect, url_for, session, flash
from app import data_access
from app.db import get_db_connection
from app.utils import login_required
from . import bp


@bp.route('/')
def index():
    user_id = session.get('user_id')
    try:
        results = data_access.get_categories()
        products = data_access.get_products()
        categories = {}
        for row in results:
            cat_id = row['category_id']
            if cat_id not in categories:
                categories[cat_id] = {'name': row['category_name'], 'subcategories': []}
            if row['subcategory_id']:
                categories[cat_id]['subcategories'].append({
                    'id': row['subcategory_id'],
                    'name': row['subcategory_name']
                })
        return render_template('products/product_list.html', products=products, user_id=user_id, categories=categories)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/products')
def product_list():
    sort_by = request.args.get('sort_by', 'name_asc')
    category_id = request.args.get('category_id')

    sort_options = {
        'price_asc': 'p.cost ASC',
        'price_desc': 'p.cost DESC',
        'name_asc': 'p.name ASC',
        'name_desc': 'p.name DESC'
    }
    order_by = sort_options.get(sort_by, 'p.name ASC')

    try:
        categories = data_access.get_categories()
        if category_id:
            subcategory_ids = [category_id]
            subcategories = data_access.get_subcategories(category_id)
            while subcategories:
                new_subcategories = []
                for sub in subcategories:
                    subcategory_ids.append(sub['c_id'])
                    new_subcategories.extend(data_access.get_subcategories(sub['c_id']))
                subcategories = new_subcategories
            products = data_access.get_products_by_category(subcategory_ids, order_by)
        else:
            products = data_access.get_all_products(order_by)
        return render_template('products/product_list.html', products=products, categories=categories,
                               sort_by=sort_by, category_id=category_id)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    user_id = session.get('user_id')
    try:
        product = data_access.get_product_details(product_id)
        if not product:
            return "Product not found", 404
        reviews = data_access.get_product_reviews(product_id)
        product_in_wishlist = False
        if user_id:
            product_in_wishlist = data_access.is_product_in_wishlist(user_id, product_id)
        return render_template('products/product_detail.html', product=product, reviews=reviews,
                               user_id=user_id, product_in_wishlist=product_in_wishlist)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if query:
        try:
            products = data_access.search_products(query)
            return render_template('products/search_results.html', query=query, products=products)
        except Exception as e:
            return f"Database error: {str(e)}", 500
    return render_template('products/search_results.html', query=query, products=[])


@bp.route('/seller/shop')
def seller_shop():
    seller_id = request.args.get('seller_id')
    if not seller_id:
        return "Seller ID is required", 400
    try:
        seller = data_access.get_seller_by_id(seller_id)
        if not seller:
            return "Seller not found", 404
        products = data_access.get_products_by_seller_id(seller_id)
        return render_template('products/seller_shop.html', seller=seller, products=products)
    except Exception as e:
        return f"Database error: {str(e)}", 500


@bp.route('/add_product/<int:user_id>', methods=['POST'])
@login_required
def add_product(user_id):
    name = request.form.get('name')
    cost = request.form.get('cost')
    available_copies = request.form.get('available_copies')
    category_name = request.form.get('category_name')
    information = request.form.get('information')
    pict_url = request.form.get('picture_url')
    try:
        data_access.add_product_to_db(user_id, name, cost, available_copies, category_name, information, pict_url)
        flash('Product added and subscribers notified!', 'success')
        return redirect(url_for('users.user_profile', user_id=user_id))
    except ValueError as e:
        return str(e), 404
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/update_products', methods=['POST', 'GET'])
@login_required
def update_products():
    user_id = session.get('user_id')
    try:
        products = data_access.get_products_by_seller_id_for_update(user_id)
        for product in products:
            product_id = product[0]
            new_cost = request.form.get(f'cost_{product_id}')
            new_copies = request.form.get(f'copies_{product_id}')
            new_info = request.form.get(f'info_{product_id}')
            data_access.update_product(product_id, user_id, new_cost, new_copies, new_info)
        return redirect(url_for('orders.seller_orders'))
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/new_products')
@login_required
def new_products():
    user_id = session.get('user_id')
    try:
        products = data_access.get_new_products_for_user(user_id)
        return render_template('products/new_products.html', products=products)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/product_statistics/<int:user_id>', methods=['GET'])
@login_required
def product_statistics(user_id):
    try:
        user = data_access.get_user_by_id(user_id)
        if not user:
            return "User not found", 404
        stats = data_access.get_product_statistics(user_id)
        if not stats:
            return "No statistics found", 404
        return render_template('users/product_statistics.html', user=user, statistics=stats)
    except Exception as e:
        return f"Database error: {str(e)}", 500


@bp.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = session['user_id']
    try:
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT seller_id FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if product and product['seller_id'] == user_id:
                flash('You cannot review your own product!', 'warning')
                return redirect(url_for('products.product_detail', product_id=product_id))
            cursor.execute("""
                INSERT INTO Reviews (rating, product_id, reviewer, comment)
                VALUES (%s, %s, %s, %s)
            """, (rating, product_id, user_id, comment))
            conn.commit()
        return redirect(url_for('products.product_detail', product_id=product_id))
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    user_id = session['user_id']
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Reviews WHERE r_id = %s AND reviewer = %s", (review_id, user_id))
            conn.commit()
        product_id = request.form.get('product_id')
        return redirect(url_for('products.product_detail', product_id=product_id))
    except Exception as err:
        return f"Database error: {err}", 500
