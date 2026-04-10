#!/bin/bash
# OliveERP Runtime Start Script

echo "================================================="
echo ">>> OLIVE ERP PRODUCTION RUNTIME STARTING <<<"
echo "================================================="

set -e

echo "---> Applying database migrations..."
python manage.py migrate --no-input
echo "---> Migrations complete."

if [[ "$CREATE_SUPERUSER" == "true" ]]; then
    echo "---> CREATE_SUPERUSER is true. Checking for admin account..."
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || echo "---> Superuser already exists or creation failed (skipping)."
else
    echo "---> Skipping superuser creation (not requested)."
fi

echo "---> Starting Gunicorn web server on port $PORT..."
gunicorn wagtailerp.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
