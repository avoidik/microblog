from datetime import datetime, timedelta
from app import db, login
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from hashlib import md5
import jwt
from app.search import add_to_index, query_index, remove_from_index

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            result = cls.query.filter_by(id=0)
        else:
            when = [(ids[i], i) for i in range(len(ids))]
            result = cls.query.filter(cls.id.in_(ids)). \
                        order_by(db.case(when, value=cls.id))
        return result, total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            add_to_index(cls.__tablename__, obj)

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(SearchableMixin, UserMixin, db.Model):
    __searchable__ = ['username']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic',
        collection_class=set
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)

    def is_following(self, u):
        return self.followed.filter(followers.c.followed_id == u.id).count() > 0

    def follow(self, u):
        if not self.is_following(u):
            self.followed.append(u)

    def unfollow(self, u):
        if self.is_following(u):
            self.followed.remove(u)

    def followed_posts(self):
        posts = Post.query. \
                join(followers, (followers.c.followed_id == Post.user_id), isouter=True). \
                filter((followers.c.follower_id == self.id) | (Post.user_id == self.id)). \
                group_by(Post.id). \
                group_by(Post.user_id). \
                order_by(Post.timestamp.desc())
        return posts

    def followed_posts_union(self):
        followed = Post.query. \
                join(followers, (followers.c.followed_id == Post.user_id)). \
                filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        token = jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(minutes=10), 'iat': datetime.utcnow()},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token.decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        result = None
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            result = User.query.get(data['reset_password'])
        except jwt.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            pass
        return result

class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.author)

db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)

db.event.listen(db.session, 'before_commit', User.before_commit)
db.event.listen(db.session, 'after_commit', User.after_commit)
