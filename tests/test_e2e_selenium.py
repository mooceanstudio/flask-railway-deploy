"""End-to-end browser test driven by Selenium.

The app is served on a background thread with werkzeug's development server
and a real headless browser submits the feedback form. The test skips
gracefully (rather than failing) when Selenium or a Chrome/Chromium browser
is not available, so the suite stays green in browser-less environments.
"""

import os
import socket
import tempfile
import threading
import time

import pytest

from app import create_app
from app.extensions import db

selenium = pytest.importorskip("selenium")

from selenium import webdriver  # noqa: E402
from selenium.common.exceptions import WebDriverException  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _make_driver():
    """Return a headless Chrome driver or None if unavailable."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024")

    # First try Selenium Manager (bundled with Selenium 4.6+).
    try:
        return webdriver.Chrome(options=options)
    except WebDriverException:
        pass

    # Fall back to webdriver-manager if it is installed.
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception:  # noqa: BLE001 - any failure means "no browser"
        return None


@pytest.fixture()
def live_server():
    """Run the app on a background thread and yield its base URL."""
    port = _free_port()
    # A temp file DB is shared cleanly across the server and test threads.
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    application = create_app("testing")
    application.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    with application.app_context():
        db.create_all()

    server = None
    try:
        from werkzeug.serving import make_server

        server = make_server("127.0.0.1", port, application, threaded=True)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Could not start live server: {exc}")

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    # Wait for the server to accept connections.
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    thread.join(timeout=5)
    with application.app_context():
        db.drop_all()
    try:
        os.remove(db_path)
    except OSError:
        pass


def test_submit_feedback_via_browser(live_server):
    driver = _make_driver()
    if driver is None:
        pytest.skip("No Chrome/Chromium browser available for Selenium")

    try:
        driver.get(live_server)
        assert "Community Feedback Board" in driver.title

        driver.find_element(By.ID, "name").send_keys("Selenium Bot")
        driver.find_element(By.ID, "message").send_keys(
            "This message came from a real browser."
        )
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "flash-success"))
        )

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Thanks for your feedback" in body_text
        assert "Selenium Bot" in body_text
        assert "This message came from a real browser." in body_text
    finally:
        driver.quit()
