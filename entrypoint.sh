#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Seed database
echo "Seeding database..."
python manage.py seed_db || echo "Seeding skipped or failed"

# Start the main process
exec "$@"
