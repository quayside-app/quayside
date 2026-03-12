#!/bin/bash
set -e
python manage.py collectstatic --noinput
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 90 quayside.wsgi:application
