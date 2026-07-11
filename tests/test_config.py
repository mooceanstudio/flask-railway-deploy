"""Unit tests for configuration helpers."""

import pytest

from app.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    config_by_name,
    normalize_database_url,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            "postgres://user:pw@host:5432/db",
            "postgresql+psycopg2://user:pw@host:5432/db",
        ),
        (
            "postgresql://user:pw@host:5432/db",
            "postgresql+psycopg2://user:pw@host:5432/db",
        ),
        (
            "postgresql+psycopg2://user:pw@host:5432/db",
            "postgresql+psycopg2://user:pw@host:5432/db",
        ),
        ("sqlite:///local.db", "sqlite:///local.db"),
        (None, None),
        ("", ""),
    ],
)
def test_normalize_database_url(raw, expected):
    assert normalize_database_url(raw) == expected


def test_normalize_rewrites_legacy_postgres_scheme():
    url = "postgres://u:p@db.internal:5432/railway"
    result = normalize_database_url(url)
    assert result.startswith("postgresql+psycopg2://")
    assert "postgres://" not in result


def test_config_registry_contains_expected_names():
    assert config_by_name["development"] is DevelopmentConfig
    assert config_by_name["production"] is ProductionConfig
    assert config_by_name["testing"] is TestingConfig
    assert config_by_name["default"] is DevelopmentConfig


def test_testing_config_defaults():
    assert TestingConfig.TESTING is True
    assert "sqlite" in TestingConfig.SQLALCHEMY_DATABASE_URI


def test_normalize_none_returns_none():
    assert normalize_database_url(None) is None
