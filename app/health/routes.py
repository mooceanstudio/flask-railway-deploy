"""Health and readiness endpoints used by Railway's healthcheck."""

from flask import jsonify
from sqlalchemy import text

from ..extensions import db
from . import bp


@bp.route("/health", methods=["GET"])
def health():
    """Liveness probe.

    Returns 200 as long as the web process is up and able to serve
    requests. This is the endpoint wired to ``healthcheckPath`` in
    ``railway.json`` and intentionally does not touch the database, so a
    transient database blip never triggers a restart loop.
    """
    return jsonify({"status": "ok"}), 200


@bp.route("/ready", methods=["GET"])
def ready():
    """Readiness probe.

    Verifies that the database is reachable by issuing a trivial query.
    Returns 200 when the dependency is healthy and 503 otherwise, so an
    orchestrator can withhold traffic until the app can actually serve it.
    """
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - report any connectivity failure
        return (
            jsonify({"status": "unavailable", "database": str(exc)}),
            503,
        )

    return jsonify({"status": "ready", "database": "ok"}), 200
