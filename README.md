# Microblog

## Run smtp daemon
```
venv\scripts\activate
export MAIL_SERVER=localhost
export MAIL_PORT=8025
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
