import mysql.connector
from flask import g, current_app


def get_db_connection():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            host=current_app.config['DB_HOST'],
            database=current_app.config['DB_NAME'],
            raise_on_warnings=True,
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
    return g.db


def close_db_connection(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
