#!/bin/bash
# OliveERP Runtime Start Script

set -e

# Run database migrations
python manage.py migrate --no-input

# Create a superuser if requested
if [[ "$CREATE_SUPERUSER" == "true" ]]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

# Start Gunicorn
gunicorn wagtailerp.wsgi:application --workers 2 --bind 0.0.0.0:$PORT