import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_message_creation(self):
        """testing valid message creation"""
        msg = Message(
            text = "TEST MESSAGE",
            timestamp = Message.timestamp.default.arg,
            user_id = self.testuser.id
        )

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(Message.query.all()), 1)

        """testing invalid message creation"""
        msg2 = Message(
            text = "TEST MESSAGE",
            timestamp = Message.timestamp.default.arg,
            user_id = self.testuser.id
        )

        with self.assertRaises(Exception) as context:
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise Exception