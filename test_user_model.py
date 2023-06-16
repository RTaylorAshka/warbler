"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does the repr method work as expected?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertIn('testuser', repr(u))
        self.assertIn('test@test.com', repr(u))

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        
        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()

        u2.followers.append(u1)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))

        """Does is_following successfully detect when user1 is not following user2?"""

        u2.followers.remove(u1)
        db.session.commit()

        self.assertFalse(u1.is_following(u2))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        
        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()

        u1.followers.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_followed_by(u2))

        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        u1.followers.remove(u2)
        db.session.commit()

        self.assertFalse(u1.is_followed_by(u2))

        

    def test_user_create(self):
        """Does User.create successfully create a new user given valid credentials?"""

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url= User.image_url.default.arg
        )

        db.session.commit()

        self.assertEqual(len(User.query.filter_by(username = "testuser").all()), 1)

        self.assertNotEqual(u.password, "HASHED_PASSWORD")

        """Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        """invalid username"""
        User.signup(
            email="OKemail@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url= User.image_url.default.arg
        )
        
        
        with self.assertRaises(Exception) as context:
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise Exception

        """invalid email"""
        User.signup(
            email="test@test.com",
            username="OKusername",
            password="HASHED_PASSWORD",
            image_url= User.image_url.default.arg
        )
        
        
        with self.assertRaises(Exception) as context:
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise Exception
        
        """missing args"""
        User.signup(
            email=None,
            username=None,
            password="HASHED_PASSWORD",
            image_url= User.image_url.default.arg
        )
        
        
        with self.assertRaises(Exception) as context:
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise Exception

    def test_user_auth(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url= User.image_url.default.arg
        )
        
        db.session.commit()

        self.assertIsInstance(User.authenticate(u.username, "HASHED_PASSWORD"), User)

        """Does User.authenticate fail to return a user when the username is invalid?"""

        self.assertFalse(User.authenticate("invalid_username", "HASHED_PASSWORD"), User)

        """Does User.authenticate fail to return a user when the password is invalid?"""

        self.assertFalse(User.authenticate(u.username, "invalidPasword"), User)
        

