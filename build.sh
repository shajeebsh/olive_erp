#!/bin/bash
# OliveERP Build Script for Render.com

set -e

echo "---> Starting OliveERP Build Phase"
echo "---> Installing dependencies..."
pip install -r requirements.txt
echo "---> Dependencies installed."

echo "---> Collecting static files..."
python manage.py collectstatic --no-input
echo "---> Static files collected."

echo "---> Build Phase Finished Successfully."