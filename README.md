# Microblog

Based on [tutorial](https://learn.miguelgrinberg.com)

Improvements here are following:
- Seeding database via flask CLI
- Different query for followed_posts()
- Additional errors handler
- Few custom helpers for Views and Controllers
- Complete Vagrant configuration

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
3. Destroy
```
vagrant destroy -f
```