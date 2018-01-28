web: flask translate compile; flask db upgrade; flask seed --no-destructive; gunicorn microblog:app
worker: rq worker microblog-tasks