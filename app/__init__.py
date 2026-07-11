"""Application factory for the Community Feedback Board.

The factory pattern keeps the app importable without side effects, which is
essential for testing and for the ``gunicorn "app:create_app()"`` entry point
used in production on Railway.
"""

import os

from flask import Flask, jsonify, render_template, request

from .config import config_by_name
from .extensions import db, migrate


def _select_config_name() -> str:
    """Pick a configuration name from the environment."""
    name = os.environ.get("APP_SETTINGS") or os.environ.get("FLASK_ENV")
    if name in config_by_name:
        return name
    return "default"


def create_app(config_name: str | None = None) -> Flask:
    """Build and configure a Flask application instance."""
    app = Flask(__name__)

    config_name = config_name or _select_config_name()
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Ensure the instance folder exists for the SQLite dev/prod fallback.
    os.makedirs(os.path.join(os.getcwd(), "instance"), exist_ok=True)

    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_shell_context(app)

    return app


def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)


def _register_blueprints(app: Flask) -> None:
    # Import inside the function to avoid importing models before the app
    # exists, which keeps the factory free of import-time side effects.
    from .api import bp as api_bp
    from .health import bp as health_bp
    from .main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(health_bp)


def _wants_json() -> bool:
    return request.path.startswith("/api") or request.accept_mimetypes.best == (
        "application/json"
    )


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error):  # noqa: ANN001
        if _wants_json():
            return jsonify({"error": "not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):  # noqa: ANN001
        if _wants_json():
            return jsonify({"error": "internal server error"}), 500
        return render_template("500.html"), 500


def _register_shell_context(app: Flask) -> None:
    from .models import Feedback

    @app.shell_context_processor
    def shell_context():  # noqa: ANN202
        return {"db": db, "Feedback": Feedback}
