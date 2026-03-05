from flask import Blueprint

bp = Blueprint('products', __name__)

from . import routes  # noqa: E402, F401
