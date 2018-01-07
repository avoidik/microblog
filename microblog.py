from app import app, db, cli
from app.models import User, Post

@app.template_filter("show_all_attrs")
def show_all_attrs(value):
    res = []
    for k in dir(value):
        res.append('%r %r\n' % (k, getattr(value, k)))
    return '\n'.join(res)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
