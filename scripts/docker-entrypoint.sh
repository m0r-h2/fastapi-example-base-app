#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python scripts/wait_for_db.py; do
  sleep 1
done

echo "Applying database migrations..."
alembic -c app/alembic.ini upgrade head

echo "Starting application..."
exec uvicorn app.main:main_app --host 0.0.0.0 --port 8000
