#!/bin/bash
# OliveERP Build Script for Render.com

set -e

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

# Create a superuser if requested via Render Environment Variables
if [[ "$CREATE_SUPERUSER" == "true" ]]; then
    echo "Attempting to create superuser..."
    python manage.py createsuperuser \
        --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" || true
fi
