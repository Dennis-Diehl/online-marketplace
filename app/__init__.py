import logging
from flask import Flask, render_template
from .config import DevelopmentConfig
from .db import close_db_connection


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    app.teardown_appcontext(close_db_connection)

    from .blueprints.auth import bp as auth_bp
    from .blueprints.products import bp as products_bp
    from .blueprints.cart import bp as cart_bp
    from .blueprints.orders import bp as orders_bp
    from .blueprints.wishlist import bp as wishlist_bp
    from .blueprints.messaging import bp as messaging_bp
    from .blueprints.users import bp as users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(users_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    logging.basicConfig(level=logging.INFO)

    return app
