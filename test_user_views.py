import os
from unittest import TestCase

from models import db, connect_db, Message, User


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser2 = User.signup(username="anotheruser",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        msg1 = Message(text = 'TEST MESSAGE ONE', user_id = self.testuser.id)
        msg2 = Message(text = 'TEST MESSAGE TWO', user_id = self.testuser.id)

        self.testuser.messages.append(msg1)
        self.testuser2.messages.append(msg2)

        db.session.commit()

    def test_users(self):
        """Can we see both users on all users page?"""

        with self.client as c:
            
            resp = c.get("/users")
            html = resp.get_data(as_text = True)

            self.assertIn('testuser', html)
            self.assertIn('anotheruser', html)

    def test_search_user(self):
        """Can we see searched user on all users page?"""

        with self.client as c:
            
            resp = c.get("/users", query_string = {'q' : 'anotheruser'})
            html = resp.get_data(as_text = True)

            self.assertIn('anotheruser', html)
            self.assertNotIn('testuser', html)

    def test_user_details(self):
        """Can user see detail page of user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text = True)

            self.assertIn(self.testuser.username, html)
            self.assertIn("Edit Profile", html)

            """Can user see edit profile button of other user?"""

            resp = c.get(f"/users/{self.testuser2.id}")
            html = resp.get_data(as_text = True)
            
            self.assertNotIn("Edit Profile", html)

    def test_user_follow(self):
        """can we see user1 follow user2?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/follow/{self.testuser2.id}")
            self.assertEqual(resp.status_code, 302)

            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text = True)

            self.assertIn('@anotheruser', html)

            resp = c.get(f"/users/{self.testuser2.id}/followers")
            html = resp.get_data(as_text = True)

            self.assertIn('@testuser', html)

            """can we see user1 unfollow user2?"""

            resp = c.post(f"/users/stop-following/{self.testuser2.id}")
            self.assertEqual(resp.status_code, 302)

            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text = True)

            self.assertNotIn('@anotheruser', html)

    def test_user_like(self):
        """can user1 like user2's message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message.query.filter_by(user_id = self.testuser2.id).one()

            c.post(f"/users/add_like/{msg.id}")

            resp = c.get(f"/users/{self.testuser.id}/likes")
            html = resp.get_data(as_text = True)

            self.assertIn(msg, self.testuser.likes)
            self.assertIn('TEST MESSAGE TWO', html)

            """can user1 unlike user2's message?"""
            
            c.post(f"/users/add_like/{msg.id}")

            resp = c.get(f"/users/{self.testuser.id}/likes")
            html = resp.get_data(as_text = True)

            self.assertNotIn('TEST MESSAGE TWO', html)

    def test_user_delete(self):
        """can user delete their account?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message.query.filter_by(user_id = self.testuser2.id).one()
            c.post(f"/users/add_like/{msg.id}")
            c.post(f"/users/follow/{self.testuser2.id}")

            c.post("/users/delete")

            self.assertEqual(len(User.query.filter_by(username = 'testuser').all()), 0)