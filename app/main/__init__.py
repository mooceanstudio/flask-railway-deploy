"""Server-rendered web pages blueprint."""

from flask import Blueprint

bp = Blueprint("main", __name__)

from . import routes  # noqa: E402,F401  (register routes on import)
