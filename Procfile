web: gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2} --access-logfile - --error-logfile -
release: flask db upgrade
