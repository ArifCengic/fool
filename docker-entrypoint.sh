#!/bin/bash

echo "Collect static files"
# python manage.py collectstatic --noinput

echo "Apply DB migrations"
python manage.py migrate

echo "Load Redis date "
python manage.py populate_redis

echo "Starting server"
python manage.py runserver 0.0.0.0:8000