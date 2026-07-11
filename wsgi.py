"""WSGI entry point.

Allows running with `gunicorn wsgi:app` in addition to the factory form
`gunicorn "app:create_app()"` used in the Procfile and start.sh.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
