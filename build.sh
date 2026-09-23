#!/usr/bin/env bash
# Render build script for AgriConnect
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Seed database
python manage.py seed_phase2
