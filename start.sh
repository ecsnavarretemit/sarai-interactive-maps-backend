#!/usr/bin/env bash

# Start Gunicorn processes
echo "Starting Gunicorn."

exec gunicorn -c gunicorn.py app.wsgi:application --bind unix:sarai_maps_api.sock


