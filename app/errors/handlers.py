from flask import render_template, current_app
from app import db
from app.errors import bp
from werkzeug.exceptions import HTTPException

current_app.config['TRAP_HTTP_EXCEPTIONS'] = True

@bp.app_errorhandler(HTTPException)
def generic_http_exception_handler(error):
    msg = [str(x) for x in error.args]
    where = error.__class__.__name__
    code = error.status_code
    return render_template("errors/generic.html", where=where, code=code, msg=msg), error.code

#@bp.app_errorhandler(404)
#def not_found_error(error):
#    return render_template("errors/404.html", error=error), 404

#@bp.app_errorhandler(500)
#def internal_error(error):
#    db.session.rollback()
#    return render_template("errors/500.html", error=error), 500
