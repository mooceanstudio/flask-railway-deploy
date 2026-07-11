"""Shared pytest fixtures."""

import os

import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app():
    """Create a fresh application configured for testing.

    Uses TEST_DATABASE_URL if provided (so CI can point this at a Postgres
    service container) and falls back to an in-memory SQLite database.
    """
    application = create_app("testing")

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def seed_feedback(app):
    """Insert a batch of feedback rows and return them."""
    from app.models import Feedback

    entries = []
    with app.app_context():
        for i in range(1, 26):
            entry = Feedback(name=f"User {i}", message=f"Message number {i}")
            _db.session.add(entry)
            entries.append(entry)
        _db.session.commit()
    return entries
