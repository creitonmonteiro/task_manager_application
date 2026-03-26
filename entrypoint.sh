#!/bin/sh

set -e

export DATABASE_URL="postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@fastzero_database:5432/${POSTGRES_DB}"

poetry run alembic upgrade head

exec poetry run uvicorn --host 0.0.0.0 --port 8000 fastapi_zero.app:app