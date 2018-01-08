#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Post
from config import Config
from hashlib import md5
from sqlalchemy.exc import IntegrityError

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hash(self):
        u = User(username='susan')
        u.set_password('demo')
        self.assertFalse(u.check_password('wrong'))
        self.assertTrue(u.check_password('demo'))

    def test_avatar(self):
        u = User(username='susan', email='susan@sample.com')
        digest = md5("susan@sample.com".encode("utf-8")).hexdigest()
        self.assertEqual(u.avatar(128), "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, 128))

    def test_integrity(self):
        u = User()

        with self.assertRaisesRegex(IntegrityError, 'NOT NULL constraint failed'):
            db.session.add(u)
            db.session.commit()

        db.session.rollback()
        u.username='susan'
        u.email='susan@sample.com'

        with self.assertRaisesRegex(IntegrityError, 'NOT NULL constraint failed'):
            db.session.add(u)
            db.session.commit()

    def test_follow(self):
        u1 = User(username='john', email='john@sample.com')
        u2 = User(username='susan', email='susan@sample.com')
        u1.set_password("john")
        u2.set_password("susan")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
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

        self.assertEqual(u1.followed_posts().count(), 3)
        self.assertEqual(u2.followed_posts().count(), 2)
        self.assertEqual(u3.followed_posts().count(), 2)
        self.assertEqual(u4.followed_posts().count(), 1)

        f1 = u1.followed_posts().all() # john should have own p1, susan p2, david p4 posts
        f2 = u2.followed_posts().all() # susan should have own p2, mary p3 posts
        f3 = u3.followed_posts().all() # mary should have own p3, david p4 posts
        f4 = u4.followed_posts().all() # david should have own p4 posts
        self.assertEqual(f1, [p1, p2, p4])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)
