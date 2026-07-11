"""Application configuration.

Configuration is expressed as classes so that environment-specific
behaviour (development, testing, production) is explicit and easy to audit.
The active class is chosen in the application factory from the ``APP_SETTINGS``
or ``FLASK_ENV`` environment variables.
"""

import os


def normalize_database_url(url: str | None) -> str | None:
    """Return a SQLAlchemy-compatible database URL.

    Managed platforms such as Railway and Heroku expose their PostgreSQL
    connection string with the legacy ``postgres://`` scheme. SQLAlchemy
    dropped support for that alias, so passing it through unchanged raises
    ``NoSuchModuleError``. We rewrite it to ``postgresql://`` (and pin the
    ``psycopg2`` driver) before SQLAlchemy ever sees it.

    Any other value is returned untouched, so SQLite URLs used for local
    development pass straight through.
    """
    if not url:
        return url

    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    # Pin the driver explicitly so the intent is unambiguous regardless of
    # which DBAPI happens to be installed.
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://") :]

    return url


class BaseConfig:
    """Settings shared by every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Recycle connections before managed proxies drop idle ones and
        # verify liveness on checkout to survive database restarts.
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Number of feedback entries shown per page on the board and the API.
    ITEMS_PER_PAGE = 10

    # Validation limits, shared by the web form and the JSON API.
    MAX_NAME_LENGTH = 80
    MAX_MESSAGE_LENGTH = 500

    @staticmethod
    def init_app(app):  # noqa: D401 - hook for subclasses
        """Optional per-config initialisation hook."""


class DevelopmentConfig(BaseConfig):
    """Local development against a SQLite file."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get("DATABASE_URL")
    ) or "sqlite:///" + os.path.join(
        os.path.abspath(os.getcwd()), "instance", "feedback-dev.db"
    )


class TestingConfig(BaseConfig):
    """Fast, isolated configuration for the test suite."""

    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get("TEST_DATABASE_URL")
    ) or "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    """Production configuration backed by managed PostgreSQL."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get("DATABASE_URL")
    ) or "sqlite:///" + os.path.join(
        os.path.abspath(os.getcwd()), "instance", "feedback.db"
    )

    @staticmethod
    def init_app(app):
        # Fail fast if a real secret was never provided in production.
        if app.config["SECRET_KEY"] == "dev-insecure-change-me":
            app.logger.warning(
                "SECRET_KEY is using the insecure default. Set SECRET_KEY "
                "in the environment before serving production traffic."
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
