#!/bin/sh

wait_for_connection() {
  echo "Waiting for connection $1:$2 ..."
  until nc -z $1 $2; do
    sleep 2
  done
}

wait_for_connection "${DB_TCP_ADDR}" "${DB_TCP_PORT}"

wait_for_connection "${ES_TCP_ADDR}" "${ES_TCP_PORT}"

source venv/bin/activate
flask translate compile
flask db upgrade
flask seed --no-destructive
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app
