import unittest
from app import app, db
from app.models import User
from hashlib import md5
from sqlalchemy.exc import IntegrityError

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

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
        u = User(username='susan', email='susan@sample.com')

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
        #self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        #self.assertEqual(u1.followed.count(), 0)
        #self.assertEqual(u2.followers.count(), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
