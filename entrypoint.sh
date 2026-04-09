#!/bin/sh

set -e

POSTGRES_HOST="${POSTGRES_HOST:-task_manager_database}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

if [ -z "$DATABASE_URL" ]; then
	export DATABASE_URL="postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
fi

if [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_DB" ]; then
	until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
		echo "Waiting for database at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
		sleep 2
	done
fi

poetry run alembic upgrade head

exec poetry run uvicorn --host 0.0.0.0 --port 8000 task_manager.app:app