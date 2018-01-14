#!/bin/sh

wait_for_connection() {
  echo "Waiting for connection $1:$2 ..."
  until nc -z $1 $2; do
    sleep 2
  done
}

case "${DATABASE_TYPE}" in
    "postgresql") wait_for_connection "${DB_PORT_5432_TCP_ADDR}" "${DB_PORT_5432_TCP_PORT}" ;;
    "mysql") wait_for_connection "${DB_PORT_3306_TCP_ADDR}" "${DB_PORT_3306_TCP_PORT}" ;;
    *) ;;
esac

wait_for_connection "${ES_PORT_9200_TCP_ADDR}" "${ES_PORT_9200_TCP_PORT}"

source venv/bin/activate
flask translate compile
flask db upgrade
flask seed --no-destructive
exec gunicorn -b :5000 --access-logfile - --error-logfile - microblog:app
