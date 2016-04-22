from google.appengine.ext import testbed
import unittest
import webtest
import main


class HandlerTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.setup_env(USER_EMAIL='tester_1@sweetvision.com',
                               USER_ID='1',
                               USER_IS_ADMIN='0',
                               overwrite=True)
        self.testapp = webtest.TestApp(main.app)

    def tearDown(self):
        self.testbed.deactivate()

    def test_sample_request(self):
        """Test a GET / and check a 200 status"""
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
