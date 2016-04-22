from base import BasePageHandler


class BaseRegisteredUserPageHandler(BasePageHandler):
    def __init__(self, request=None, response=None):
        super(BaseRegisteredUserPageHandler, self).__init__(request, response)
        if self.logged_in and not self.user:
            self.redirect('/register_user')
