import re

from base import BasePageHandler

from google.appengine.api import users


class BaseAuthenticatedUserPageHandler(BasePageHandler):
    def __init__(self, request=None, response=None):
        super(BaseAuthenticatedUserPageHandler, self).__init__(request, response)
        if not self.redirected and self.google_user is None:
            request_path = request.path
            if request_path is None or re.match(r"^\s*$", request_path):
                request_path = '/'
            self.redirected = True
            self.redirect(users.create_login_url(request_path))
