#!/bin/sh
set -e

# --- Configuration ---
DB_HOST=${DATABASE_HOST:-db}       # default to "db" if DATABASE_HOST not set
DB_PORT=${DATABASE_PORT:-5432}    # default to 5432 if DATABASE_PORT not set

# --- Wait for Postgres to be ready ---
echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Postgres is unavailable - sleeping 1s"
  sleep 1
done
echo "Postgres is up - continuing..."

# --- Run database migrations ---
echo "Running Alembic migrations..."
alembic upgrade head

# --- Execute the main container command ---
exec "$@"
