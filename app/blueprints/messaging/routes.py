from flask import render_template, request, redirect, url_for, session, flash
from app import data_access
from app.db import get_db_connection
from app.utils import login_required
from . import bp


@bp.route('/messages')
@login_required
def messages():
    user_id = session['user_id']
    try:
        sellers = data_access.get_sellers_with_messages(user_id)
        return render_template('messaging/messages_overview.html', sellers=sellers)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/messages/<int:seller_id>')
@login_required
def view_chat(seller_id):
    user_id = session['user_id']
    try:
        msgs = data_access.get_chat_messages(user_id, seller_id)
        chat = {
            'seller_id': seller_id,
            'seller_name': msgs[0]['seller_name'] if msgs else 'Unknown',
            'messages': [
                {
                    'content': m['message'],
                    'timestamp': m['sending_date'],
                    'sender': 'user' if m['sender_id'] == user_id else 'seller'
                }
                for m in msgs
            ]
        }
        return render_template('messaging/chat.html', chat=chat)
    except Exception as err:
        return f"Database error: {err}", 500


@bp.route('/messages/send/<int:seller_id>', methods=['POST'])
@login_required
def send_message(seller_id):
    content = request.form.get('content')
    user_id = session['user_id']
    if content:
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Messaging (message, sender_id, receiver_id) VALUES (%s, %s, %s)
                """, (content, user_id, seller_id))
                conn.commit()
            flash('Message sent successfully!', 'success')
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    else:
        flash('Message content cannot be empty!', 'danger')
    return redirect(url_for('messaging.view_chat', seller_id=seller_id))


@bp.route('/messages/start_chat', methods=['POST'])
@login_required
def start_chat():
    receiver_name = request.form.get('receiver_name')
    sender_id = session['user_id']
    if receiver_name:
        try:
            conn = get_db_connection()
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT user_id FROM Users WHERE username = %s", (receiver_name,))
                receiver = cursor.fetchone()
                if not receiver:
                    flash('User not found.', 'danger')
                    return redirect(url_for('messaging.messages'))
                receiver_id = receiver['user_id']
                cursor.execute("""
                    SELECT * FROM Messaging
                    WHERE (sender_id = %s AND receiver_id = %s)
                       OR (sender_id = %s AND receiver_id = %s)
                """, (sender_id, receiver_id, receiver_id, sender_id))
                if cursor.fetchone():
                    flash('Chat already exists!', 'warning')
                else:
                    cursor.execute("""
                        INSERT INTO Messaging (message, sender_id, receiver_id) VALUES (%s, %s, %s)
                    """, ('', sender_id, receiver_id))
                    conn.commit()
                    flash('New chat started successfully!', 'success')
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    else:
        flash('Please enter a valid username.', 'danger')
    return redirect(url_for('messaging.messages'))
