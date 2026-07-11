#!/usr/bin/env bash
#
# Production entrypoint used by Railway (via railway.json / Dockerfile).
#
# 1. Apply any outstanding Alembic migrations so the schema always matches
#    the deployed code on a fresh or existing PostgreSQL database.
# 2. Start gunicorn bound to 0.0.0.0 and the platform-provided $PORT.
#
set -euo pipefail

# Railway injects $PORT; default to 8000 for local `./start.sh` runs.
export PORT="${PORT:-8000}"
export FLASK_APP="${FLASK_APP:-app:create_app}"

echo "==> Applying database migrations (flask db upgrade)"
flask db upgrade

echo "==> Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn "app:create_app()" \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --access-logfile - \
    --error-logfile -
