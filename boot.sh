#!/bin/sh
source venv/bin/activate
flask translate compile
flask db upgrade
flask seed --no-destructive
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app
