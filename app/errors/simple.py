from app import db
from flask_babel import _
from flask import render_template
from werkzeug.exceptions import default_exceptions

def _handle_http_exception(error):
    db.session.rollback()
    msg = error.description
    where = error.__class__.__name__
    code = error.code
    return render_template("errors/generic.html", msg=msg, where=where, code=code), error.code

def set_error_handler(app):
    for code in default_exceptions:
        app.errorhandler(code)(_handle_http_exception)
