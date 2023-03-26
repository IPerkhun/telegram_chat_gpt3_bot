
import unittest
import os

from db_utils.user_db_manager import UserDB, User

class UserDBTest(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for testing
        self.db_path = 'db_utils/db/test.db'
        self.db = UserDB.get_instance(self.db_path)

    def test_create_user(self):
        # Create a new user and add to the database
        user = User(id='user1', tg_api_key='key1', open_ai_password='password1', open_ai_login='login1', open_ai_api_key='api_key1', active=True)
        self.db.create_user(user)

        # Retrieve the user from the database and check if the values match
        retrieved_user = self.db.get_user_by_open_ai_login('login1')
        self.assertEqual(retrieved_user.id, 'user1')
        self.assertEqual(retrieved_user.tg_api_key, 'key1')
        self.assertEqual(retrieved_user.open_ai_password, 'password1')
        self.assertEqual(retrieved_user.open_ai_login, 'login1')
        self.assertEqual(retrieved_user.open_ai_api_key, 'api_key1')
        self.assertEqual(retrieved_user.active, True)

    def test_update_user_status(self):
        # Create a new user and add to the database
        user = User(id='user2', tg_api_key='key2', open_ai_password='password1', open_ai_login='login2', open_ai_api_key='api_key2', active=True)
        self.db.create_user(user)

        # Update the user's status
        self.db.update_user_status('user2', False)

        # Retrieve the user from the database and check if the active status is updated
        retrieved_user = self.db.get_user_by_open_ai_login('login2')
        self.assertEqual(retrieved_user.active, False)

    def test_remove_user(self):
        # Create a new user and add to the database
        user = User(id='user3', tg_api_key='key3', open_ai_password='password1', open_ai_login='login3', open_ai_api_key='api_key3', active=True)
        self.db.create_user(user)

        # Remove the user from the database
        self.db.remove_user('user3')

        # Try to retrieve the removed user from the database and check if it's None
        retrieved_user = self.db.get_user_by_open_ai_login('login3')
        self.assertIsNone(retrieved_user)