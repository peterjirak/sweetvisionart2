import re
import urllib

from base_authenticated_user_handler import BaseAuthenticatedUserPageHandler


class BaseRegisteredUserPageHandler(BaseAuthenticatedUserPageHandler):
    def __init__(self, request=None, response=None):
        super(BaseRegisteredUserPageHandler, self).__init__(request, response)
        if (not hasattr(self, 'no_redirect') or not self.no_redirect) and \
                (not self.redirected and self.google_user and not self.application_user):
            # We require user registration, but user registration has not yet occurred.
            # Trigger redirection to get the user to register.
            request_path = request.path
            if request_path is None or re.match(r"^\s*$", request_path):
                request_path = '/'

            application_url = self.request.application_url
            if not re.match(r"^.*$", application_url):
                application_url += '/'
            if request_path != '/':
                application_url += request_path

            self.redirected = True
            self.redirect('/register_user?continue=' + urllib.quote(application_url, safe=''))
