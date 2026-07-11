# syntax=docker/dockerfile:1

# --- Stage 1: build wheels for all dependencies -----------------------------
FROM python:3.12.4-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Build tools needed to compile psycopg2 wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt


# --- Stage 2: lean runtime image --------------------------------------------
FROM python:3.12.4-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app:create_app \
    APP_SETTINGS=production \
    PORT=8000

# libpq is required at runtime by psycopg2.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser

WORKDIR /app

# Install dependencies from the prebuilt wheels.
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copy the application source and make the entrypoint executable.
COPY . .
RUN chmod +x ./start.sh && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# start.sh runs `flask db upgrade` then launches gunicorn bound to $PORT.
CMD ["./start.sh"]
