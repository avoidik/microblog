# Microblog

Based on [tutorial](https://learn.miguelgrinberg.com)

Improvements here are following:
- Seeding database via flask CLI
- Different query for followed_posts()
- Additional errors handler
- Few custom helpers for Views and Controllers
- Complete Vagrant configuration
- Additional database constraints
- Additional tests
- Complete docker-compose infrastructure

## Run smtp daemon
```
venv\scripts\activate
export MAIL_SERVER=localhost
export MAIL_PORT=8025
...
python -m smtpd -n -c DebuggingServer localhost:8025
```
## Gmail account
```
venv\scripts\activate
export MAIL_SERVER=smtp.googlemail.com
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME=<your-gmail-username>
export MAIL_PASSWORD=<your-gmail-password>
```
## Babel
```
pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel init -i messages.pot -d app/translations -l ru
pybabel compile -d app/translations
pybabel update -i messages.pot -d app/translations
```
### Test Redis
Start the worker
```
rq worker microblog-tasks
```
Enqueue the task
```
from redis import Redis
import rq
queue = rq.Queue('microblog-tasks', connection=Redis.from_url('redis://'))
job = queue.enqueue('app.tasks.example', 10) # func, param
job.get_id()
job.refresh()
job.meta.get('progress', 0)
dir(job)
```
### Test Elasticsearch
```
from elasticsearch import Elasticsearch
es = Elasticsearch('http://localhost:9200')
es.index(index='my_index', doc_type='my_index', id=1, body={'text': 'this is a test'})
es.index(index='my_index', doc_type='my_index', id=2, body={'text': 'this is a second test'})
es.search(index='my_index', doc_type='my_index', body={'query': {'match': {'text': 'this is'}}})
es.indices.delete('my_index')
```
Or directly with curl
```
curl -XPOST 'localhost:9200/_search?pretty' -d '{"query":{"multi_match":{"query":"this is","fields":["*"],"lenient":true}},"size":15,"from":0}'
```
## Vagrant
1. Start
```
vagrant up
```
2. Play (accept self-signed certificate)
```
http://192.168.33.10/
```
There are four built-in users:
```
john
susan
mary
david
```
The password is the same as the login.

3. Destroy
```
vagrant destroy -f
```
## Heroku
```
git clone ...
heroku login
heroku apps:create flask-microblog
git remote -v
heroku addons:add heroku-postgresql:hobby-dev
heroku config:set LOG_TO_STDOUT=1
heroku addons:create searchbox:starter # elasticsearch addon
heroku addons:create heroku-redis:hobby-dev # redis addon
heroku config:get SEARCHBOX_URL
heroku config:set ELASTICSEARCH_URL=...
heroku config:set FLASK_APP=microblog.py
...
heroku ps:scale worker=1
```
Heroku addons requires validated account (linked credit-card), but they're on a free-plan (without expenses)
## Docker
```
docker-machine create microblog
docker-machine env microblog
docker build -t microblog:latest .
docker run --name microblog -d -p 8000:5000 --rm \
    -e SECRET_KEY=my-secret-key \
    -e MAIL_SERVER=smtp.googlemail.com \
    -e MAIL_PORT=587 \
    -e MAIL_USE_TLS=true \
    -e MAIL_USERNAME=<your-gmail-username> \
    -e MAIL_PASSWORD=<your-gmail-password> \
    microblog:latest
docker stop microblog
docker rmi microblog
docker-machine kill microblog
docker-machine env -u
```
## Docker compose
Create infrastructure
```
scripts/create-machine.sh
scripts/create-network.sh
scripts/up-compose.sh docker-compose.yml
```
Destroy infrastructure (soft)
```
scripts/prune.sh
scripts/down-compose.sh docker-compose.yml
scripts/kill-machine.sh
```
Destroy infrastructure (hard)
```
scripts/kill-machine.sh
```