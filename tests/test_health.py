"""Tests for the health and readiness probes."""


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_ready_returns_ok_when_db_reachable(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"


def test_ready_returns_503_when_db_unreachable(client, monkeypatch):
    from app.health import routes as health_routes

    class BrokenSession:
        def execute(self, *_args, **_kwargs):
            raise RuntimeError("connection refused")

    monkeypatch.setattr(health_routes.db, "session", BrokenSession())

    resp = client.get("/ready")
    assert resp.status_code == 503
    assert resp.get_json()["status"] == "unavailable"
