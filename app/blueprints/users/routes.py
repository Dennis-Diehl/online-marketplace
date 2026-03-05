from flask import render_template, request, redirect, url_for, session, flash
from app import data_access
from app.utils import login_required
from . import bp


@bp.route('/profile/<int:user_id>', methods=['POST', 'GET'])
@login_required
def user_profile(user_id):
    try:
        user = data_access.get_user_by_id(user_id)
        if not user:
            return "User not found", 404
        seller = data_access.get_seller_by_id(user_id)
        if request.method == 'POST' and 'is_seller' in request.form and not seller:
            shopname = request.form.get('shopname')
            data_access.insert_seller(user_id, shopname)
            flash('You have been registered as a seller!', 'success')
            return redirect(url_for('users.user_profile', user_id=user_id))
        session['user_id'] = user_id
        return render_template('users/user_profile.html', user=user, seller=seller)
    except Exception as e:
        return f"Database error: {str(e)}", 500


@bp.route('/update_user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def update_profile(user_id):
    new_username = request.form.get('username')
    new_email = request.form.get('email')
    try:
        data_access.update_user_profile(user_id, new_username, new_email)
        flash('Your profile has been updated successfully', 'success')
        return redirect(url_for('users.user_profile', user_id=user_id))
    except Exception as e:
        flash(f"Database error: {str(e)}", 'error')
        return redirect(url_for('users.user_profile', user_id=user_id))


@bp.route('/buyer_statistics/<int:user_id>', methods=['GET'])
@login_required
def buyer_statistics(user_id):
    try:
        user = data_access.get_user_by_id(user_id)
        if not user:
            return "User not found", 404
        statistics = data_access.get_buyer_statistics(user_id)
        if not statistics:
            return "No statistics found", 404
        return render_template('users/buyer_statistics.html', user=user, buyer_statistics=statistics)
    except Exception as e:
        return f"Database error: {str(e)}", 500


@bp.route('/subscribe/<int:seller_id>/<int:product_id>', methods=['POST'])
@login_required
def subscribe_to_seller(seller_id, product_id):
    user_id = session['user_id']
    try:
        if data_access.get_subscribe_to_seller(user_id, seller_id):
            flash('Successfully subscribed to the seller!', 'success')
        else:
            flash('You are already subscribed to this seller!', 'info')
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
    return redirect(url_for('products.product_detail', product_id=product_id))
