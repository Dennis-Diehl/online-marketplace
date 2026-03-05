from flask import render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from app import data_access
from . import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            user = data_access.get_user_by_username(username)
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                return redirect(url_for('products.index'))
            else:
                return "Invalid username or password", 401
        except Exception as err:
            return f"Database error: {err}", 500
    return render_template('auth/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        is_seller = 'is_seller' in request.form
        shopname = request.form.get('shopname')
        website_url = request.form.get('website_url')
        try:
            user_id = data_access.register_user(username, password, email, is_seller, shopname, website_url)
            session['user_id'] = user_id
            return redirect(url_for('auth.login'))
        except Exception as err:
            return f"Database error: {err}", 500
    return render_template('auth/register.html')


@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('products.index'))
