from app import db
from app.models import User, Post, Message, Notification, Task
from datetime import datetime, timedelta
import click
import os

def register(app):
    @app.cli.group()
    def translate():
        '''Translation and localization commands.'''
        pass

    @translate.command()
    def update():
        '''Update all languages.'''
        if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
            raise RuntimeError("extract command failed")
        if os.system("pybabel update -i messages.pot -d app/translations"):
            raise RuntimeError("update command failed")
        os.remove('messages.pot')

    @translate.command()
    def compile():
        '''Compile all languages.'''
        if os.system("pybabel compile -d app/translations"):
            raise RuntimeError("compile command failed")

    @translate.command()
    @click.argument('lang')
    def init(lang):
        '''Initialize a new language.'''
        if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
            raise RuntimeError("extract command failed")
        if os.system("pybabel init -i messages.pot -d app/translations -l " + lang):
            raise RuntimeError("init command failed")
        os.remove("messages.pot")

    @app.cli.command()
    @click.option('--destructive/--no-destructive', default=False, help='Recreate DB from scratch.')
    def seed(destructive):
        '''Overwrites database with the sample data.'''

        if destructive:
            db.drop_all()
            db.create_all()

        if User.query.filter_by(username='john').first():
            app.logger.info("Seeding has been skipped")
            return

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
        p1 = Post(body="post from " + u1.username, author=u1, timestamp=now + timedelta(seconds=4), language="en")
        p2 = Post(body="post from " + u2.username, author=u2, timestamp=now + timedelta(seconds=3), language="en")
        p3 = Post(body="post from " + u3.username, author=u3, timestamp=now + timedelta(seconds=2), language="en")
        p4 = Post(body="post from " + u4.username, author=u4, timestamp=now + timedelta(seconds=1), language="en")
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2) # john follows susan
        u1.follow(u4) # john follows david
        u2.follow(u3) # susan follows mary
        u3.follow(u4) # mary follows david
        db.session.commit()

        Post.reindex()

    @app.template_filter("show_all_attrs")
    def show_all_attrs(value):
        res = []
        for k in dir(value):
            res.append('%r %r\n' % (k, getattr(value, k)))
        return '\n'.join(res)

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Post': Post, 'Message': Message,
                    'Notification': Notification, 'Task': Task}
