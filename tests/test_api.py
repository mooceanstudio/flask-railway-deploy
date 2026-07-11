"""Integration tests for the JSON REST API."""


def test_list_feedback_empty(client):
    resp = client.get("/api/feedback")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["items"] == []
    assert body["pagination"]["total"] == 0


def test_create_feedback_api(client):
    resp = client.post(
        "/api/feedback",
        json={"name": "Linus", "message": "Ship it"},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Linus"
    assert body["message"] == "Ship it"
    assert "id" in body
    assert "created_at" in body
    assert resp.headers["Location"] == "/api/feedback"


def test_create_feedback_api_trims_whitespace(client):
    resp = client.post(
        "/api/feedback",
        json={"name": "  Margaret  ", "message": "  spaced out  "},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Margaret"
    assert body["message"] == "spaced out"


def test_create_feedback_api_validation_empty(client):
    resp = client.post("/api/feedback", json={"name": "", "message": ""})
    assert resp.status_code == 400
    errors = resp.get_json()["errors"]
    assert "name" in errors
    assert "message" in errors


def test_create_feedback_api_validation_missing_body(client):
    resp = client.post("/api/feedback")
    assert resp.status_code == 400
    assert "errors" in resp.get_json()


def test_create_feedback_api_oversized(client, app):
    resp = client.post(
        "/api/feedback",
        json={
            "name": "z" * (app.config["MAX_NAME_LENGTH"] + 1),
            "message": "ok",
        },
    )
    assert resp.status_code == 400
    assert "name" in resp.get_json()["errors"]


def test_list_feedback_pagination(client, seed_feedback):
    resp = client.get("/api/feedback?page=1&per_page=10")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body["items"]) == 10
    assert body["pagination"]["total"] == 25
    assert body["pagination"]["pages"] == 3
    assert body["pagination"]["has_next"] is True
    assert body["pagination"]["has_prev"] is False

    last = client.get("/api/feedback?page=3&per_page=10")
    last_body = last.get_json()
    assert len(last_body["items"]) == 5
    assert last_body["pagination"]["has_next"] is False


def test_list_feedback_orders_newest_first(client):
    client.post("/api/feedback", json={"name": "First", "message": "1"})
    client.post("/api/feedback", json={"name": "Second", "message": "2"})

    resp = client.get("/api/feedback")
    items = resp.get_json()["items"]
    assert items[0]["name"] == "Second"
    assert items[1]["name"] == "First"


def test_per_page_is_capped(client, seed_feedback):
    resp = client.get("/api/feedback?per_page=9999")
    body = resp.get_json()
    assert body["pagination"]["per_page"] == 100
