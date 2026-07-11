"""Shared Flask extension instances.

Extensions are instantiated here without an application so they can be
imported anywhere without triggering circular imports. They are bound to
the concrete application inside the :func:`app.create_app` factory.
"""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
