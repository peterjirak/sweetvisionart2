from google.appengine.ext import testbed
import unittest
import webtest
import main
from models.user import User


class HandlerTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()
        self.testapp = webtest.TestApp(main.app)

    def tearDown(self):
        self.testbed.deactivate()

    def setup_non_registered_user(self, user_email, user_id, user_is_admin):
        self.testbed.setup_env(USER_EMAIL=user_email,
                               USER_ID=str(user_id),
                               USER_IS_ADMIN=str(user_is_admin),
                               overwrite=True)

    def test_get_main_page_without_logged_in_user(self):
        """Test a GET / and check a 200 status"""
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)

    def test_get_main_page_with_non_registered_user(self):
        """Test a GET / and check a 302 status"""
        self.setup_non_registered_user(user_email='test_user1@test.com',
                                       user_id=1,
                                       user_is_admin=0)
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 302)

    def test_get_main_page_with_registered_user(self):
        """Test a GET / and check a 200 status"""
        self.setup_non_registered_user(user_email='test_user2@test.com',
                                       user_id=2,
                                       user_is_admin=0)

        # Add a user to the datastore -- a registered user is one in the datastore:
        User.add_or_get_user(user_id=2, email='test_user2@test.com', first_name='Test2', last_name='User')
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)

    def test_register_a_user(self):

        self.setup_non_registered_user(user_email='test_user3@test.com',
                                       user_id=3,
                                       user_is_admin=0)

        response = self.testapp.post('/register_user', {'first_name': 'Test3',
                                                        'last_name': 'User'})
        self.assertEqual(response.status_int, 302)

        registered_user = User.get_user_by_id(3)

        self.assertEqual(registered_user.user_id, '3')
        self.assertEqual(registered_user.email, 'test_user3@test.com')
        self.assertEqual(registered_user.first_name, 'Test3')
        self.assertEqual(registered_user.last_name, 'User')
