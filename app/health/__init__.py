"""Liveness and readiness probe blueprint."""

from flask import Blueprint

bp = Blueprint("health", __name__)

from . import routes  # noqa: E402,F401  (register routes on import)
