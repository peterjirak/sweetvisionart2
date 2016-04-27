import re
import os
import collections

from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.api import images
import unittest
import webtest
import json
import main
from models.user import User
from models.art import Art


class HandlerTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_images_stub()
        self.testapp = webtest.TestApp(main.app)

    def tearDown(self):
        self.testbed.deactivate()

    def setup_non_registered_user(self, user_email, google_user_id, user_is_admin):
        self.testbed.setup_env(USER_EMAIL=user_email,
                               USER_ID=str(google_user_id),
                               USER_IS_ADMIN=str(user_is_admin),
                               overwrite=True)

    def test_get_main_page_without_logged_in_user(self):
        """Test a GET / and check a 200 status"""
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)

    def test_get_main_page_with_registered_user(self):
        """Test a GET / and check a 200 status"""
        self.setup_non_registered_user(user_email='test_user2@test.com',
                                       google_user_id=2,
                                       user_is_admin=0)

        # Add a user to the datastore -- a registered user is one in the datastore:
        User.add_or_get_user(google_user_id=2, email='test_user2@test.com', first_name='Test2', last_name='User')
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)

    def test_register_a_user(self):

        self.setup_non_registered_user(user_email='test_user3@test.com',
                                       google_user_id=3,
                                       user_is_admin=0)

        response = self.testapp.post('/register_user', {'first_name': 'Test3',
                                                        'last_name': 'User'})
        self.assertEqual(response.status_int, 302)

        registered_user = User.get_user_by_google_user_id(3)

        self.assertEqual(registered_user.google_user_id, '3')
        self.assertRegexpMatches(registered_user.application_user_id, r"^[A-Za-z0-9]+[A-Za-z0-9\-]+[A-Za-z0-9]$")
        self.assertGreaterEqual(len(str(registered_user.application_user_id)), 6)
        self.assertEqual(registered_user.email, 'test_user3@test.com')
        self.assertEqual(registered_user.first_name, 'Test3')
        self.assertEqual(registered_user.last_name, 'User')

    def test_accessing_register_user_page_without_authenticating_triggers_redirect(self):
        # A user has to be authenticated to access the /register_user page.
        # Test that if a user attempts to access the /register_user page without authenticating
        # that he or she is redirected to the authentication page:

        response = self.testapp.get('/register_user')

        self.assertEqual(response.status_int, 302)

        self.assertRegexpMatches(response.headers.get('Location'), r"^https://www\.google\.com/accounts/Login\?" +
                                 "continue=http%3A//testbed\.example\.com/register_user")

    def test_accessing_upload_page_triggers_login_redirect(self):
        # A user has to be authenticated and registered to access the upload page.
        # Test that if a user attempts to access the upload page without authenticating
        # that he or she is redirected to the authentication page:

        response = self.testapp.get('/upload')

        self.assertEqual(response.status_int, 302)

        self.assertRegexpMatches(response.headers.get('Location'), r"^https://www\.google\.com/accounts/Login\?" +
                                 "continue=http%3A//testbed\.example\.com/upload")

    def test_accessing_upload_page_triggers_user_registration(self):
        # A user has to be authenticated and registered to access the upload page.
        # Test that if an authenticated user attempts to access the upload page without registering
        # that he or she is redirected to the registration page:

        # Mock authenticate the user, but do not register the user:
        self.setup_non_registered_user(user_email='test_user1@test.com',
                                       google_user_id=1,
                                       user_is_admin=0)

        response = self.testapp.get('/upload')

        self.assertEqual(response.status_int, 302)
        self.assertRegexpMatches(response.headers.get('Location'), r"^https{0,1}://[^/]+/register_user\?" +
                                 "continue=http%3A%2F%2.*?%2Fupload")

    def test_uploading_an_image(self):
        # Setup a user for the test:
        self.setup_non_registered_user(user_email='test_user4@test.com',
                                       google_user_id=4,
                                       user_is_admin=0)

        # Add a user to the datastore -- a registered user is one in the datastore:
        application_user = User.add_or_get_user(google_user_id=4, email='test_user4@test.com', first_name='Test4',
                                                last_name='User')

        application_user_id = application_user.application_user_id
        if application_user_id is None or not re.match(r"^[A-Za-z0-9]+[A-Za-z0-9\-]+[A-Za-z0-9]$",
                                                       str(application_user_id)):
            self.fail("Registered user has a valid application_user_id")

        # Load test image data from test file:
        test_image_file = os.path.dirname(__file__) + '/data/image_files/yellow_daisy.jpg'

        rfh = open(test_image_file, 'r')
        image_data = rfh.read()
        rfh.close()

        # Make a POST request to the app to load the test image:
        response = self.testapp.post('/upload',
                                     params=collections.OrderedDict([('title[]', 'Yellow Daisy'),
                                                                     ('description[]', 'Photograph of a yellow daisy ' +
                                                                      'taken on a Summer photo walk.')]),
                                     upload_files=[('userfile', 'yellow_daisy.jpg', image_data)])

        # The status code should be 200 -- OK:
        self.assertEqual(response.status_int, 200)

        # The response Content-Type should be 'application/json':
        self.assertEqual(response.headers.get('Content-Type'), 'application/json')

        # Load the JSON response from the response body:
        body_text = response.body
        json_response = None
        image_key = None
        try:
            json_response = json.loads(body_text)
        except ValueError:
            self.fail("Failed to load JSON response from response body.")

        if json_response is not None:
            # Test the contents of the JSON object loaded from the response:
            self.assertTrue(isinstance(json_response, dict))

            files = json_response.get('files')
            self.assertTrue(isinstance(files, list))
            self.assertEqual(len(files), 1)
            file_arg = files[0]
            url = file_arg.get('url', '')
            self.assertRegexpMatches(file_arg.get('url'), r"^https{0,1}://.*/image/\w+$")
            self.assertRegexpMatches(file_arg.get('thumbnail_url'), r"^https{0,1}://.*/image/\w+$")
            self.assertEqual(file_arg.get('name'), 'yellow_daisy.jpg')
            self.assertEqual(file_arg.get('size'), 366536)

            image_key_match = re.match(r"^https{0,1}://.*/image/(\w+)$", url)
            if image_key_match:
                image_key = image_key_match.group(1)
        else:
            self.fail("No JSON response received from POST /upload request")

        if image_key is not None:
            # The test image should exist in the database -- check for it using the key:
            art_key = ndb.Key(urlsafe=image_key)
            art = Art.get_by_id(art_key.id())
            self.assertTrue(isinstance(art, Art))
            self.assertEqual(art.application_user_id, application_user_id)
            self.assertEqual(art.title, 'Yellow Daisy')
            self.assertEqual(art.description, 'Photograph of a yellow daisy taken on a Summer photo walk.')

            # We resize the image before adding it to the database, so before we can check the image
            # in the database against the test source, we have to resize the test source data the same way:
            resized_image_data = images.resize(image_data, 600, 600)
            self.assertEqual(art.image, resized_image_data)
        else:
            self.fail("No art key retrieved from JSON response")
