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
heroku addons:create searchbox:starter
heroku config:get SEARCHBOX_URL
heroku config:set ELASTICSEARCH_URL=...
heroku config:set FLASK_APP=microblog.py
```
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