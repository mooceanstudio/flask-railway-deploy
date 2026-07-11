"""Integration tests for the server-rendered web pages."""


def test_home_page_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Community Feedback Board" in resp.data
    assert b"Share your feedback" in resp.data


def test_empty_board_shows_placeholder(client):
    resp = client.get("/")
    assert b"No feedback yet" in resp.data


def test_create_feedback_via_form(client):
    resp = client.post(
        "/",
        data={"name": "Ada", "message": "Hello world"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Thanks for your feedback" in resp.data
    assert b"Ada" in resp.data
    assert b"Hello world" in resp.data


def test_create_feedback_redirects(client):
    resp = client.post("/", data={"name": "Grace", "message": "Nice board"})
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")


def test_form_validation_empty_fields(client):
    resp = client.post("/", data={"name": "", "message": ""})
    assert resp.status_code == 400
    assert b"Name is required" in resp.data
    assert b"Message is required" in resp.data


def test_form_validation_oversized_name(client, app):
    long_name = "x" * (app.config["MAX_NAME_LENGTH"] + 1)
    resp = client.post("/", data={"name": long_name, "message": "hi"})
    assert resp.status_code == 400
    assert b"Name must be at most" in resp.data


def test_form_validation_oversized_message(client, app):
    long_message = "y" * (app.config["MAX_MESSAGE_LENGTH"] + 1)
    resp = client.post("/", data={"name": "Bob", "message": long_message})
    assert resp.status_code == 400
    assert b"Message must be at most" in resp.data


def test_pagination_web(client, seed_feedback, app):
    per_page = app.config["ITEMS_PER_PAGE"]

    page1 = client.get("/")
    assert page1.status_code == 200
    assert b"Page 1 of" in page1.data

    page3 = client.get("/?page=3")
    assert page3.status_code == 200
    # 25 items / 10 per page => 3 pages.
    total_pages = (25 + per_page - 1) // per_page
    assert f"Page 3 of {total_pages}".encode() in page3.data
