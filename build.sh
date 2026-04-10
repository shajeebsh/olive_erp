#!/bin/bash
# OliveERP Build Script for Render.com

set -e

pip install -r requirements.txt

python manage.py collectstatic --no-input