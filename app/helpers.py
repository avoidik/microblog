from flask import flash
from flask_babel import _

def flash_all_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(_("Error in the %(field)s field - %(msg)s", \
                    field=getattr(form, field).label.text, \
                    msg=error)
            )

