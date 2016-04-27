import re

from base import BasePageHandler

from google.appengine.api import users


class BaseAuthenticatedUserPageHandler(BasePageHandler):
    def __init__(self, request=None, response=None):
        super(BaseAuthenticatedUserPageHandler, self).__init__(request, response)
        if (not hasattr(self, 'no_redirect') or not self.no_redirect) and \
                (not self.redirected and self.google_user is None):
            # We require authentication, but authentication has not yet occurred.
            # Trigger redirection to get the user to authenticate:
            request_path = request.path
            if request_path is None or re.match(r"^\s*$", request_path):
                request_path = '/'

            self.redirected = True
            self.redirect(users.create_login_url(request_path))
