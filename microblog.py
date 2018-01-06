from app import app, db
from app.models import User, Post
from datetime import datetime, timedelta
from sqlalchemy.engine import reflection
import click

@app.template_filter("show_all_attrs")
def show_all_attrs(value):
    res = []
    for k in dir(value):
        res.append('%r %r\n' % (k, getattr(value, k)))
    return '\n'.join(res)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

@app.cli.command()
@click.option('--destructive', is_flag=True, default=False, help='Recreate DB from scratch.', prompt="Drop database?")
def seed(destructive=False):
    '''Overwrites database with the sample data.'''

    if destructive:
        db.drop_all()
        db.create_all()

    u1 = User(username='john', email='john@sample.com')
    u2 = User(username='susan', email='susan@sample.com')
    u3 = User(username='mary', email='mary@sample.com')
    u4 = User(username='david', email='david@sample.com')
    u1.set_password("john")
    u2.set_password("susan")
    u3.set_password("mary")
    u4.set_password("david")
    db.session.add_all([u1, u2, u3, u4])

    now = datetime.utcnow()
    p1 = Post(body="post from " + u1.username, author=u1, timestamp=now + timedelta(seconds=4))
    p2 = Post(body="post from " + u2.username, author=u2, timestamp=now + timedelta(seconds=3))
    p3 = Post(body="post from " + u3.username, author=u3, timestamp=now + timedelta(seconds=2))
    p4 = Post(body="post from " + u4.username, author=u4, timestamp=now + timedelta(seconds=1))
    db.session.add_all([p1, p2, p3, p4])
    db.session.commit()

    u1.follow(u2) # john follows susan
    u1.follow(u4) # john follows david
    u2.follow(u3) # susan follows mary
    u3.follow(u4) # mary follows david
    db.session.commit()
