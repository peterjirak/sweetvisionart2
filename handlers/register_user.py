import re

from google.appengine.api import users
from google.appengine.ext import ndb

from handlers.base import BasePageHandler
from models.user import User


class RegisterUserHandler(BasePageHandler):
    def get(self):
        if not self.logged_in:
            # Must login using Google Auth before registering:
            return self.redirect(users.create_login_url(self.request.uri))
        elif self.user is not None:
            # User is logged in and already registered, do not re-register:
            return self.redirect('/')

        # Get email from Google Auth user object if available:
        if self.current_user.email():
            email = self.current_user.email()
        else:
            email = None

        self.template_values['email'] = email

        template = self.get_template('templates/register_user.html')
        self.response.write(template.render(self.template_values))

    def post(self):
        if not self.logged_in:
            # Must login using Google Auth before registering:
            self.redirect(users.create_login_url(self.request.uri))
        elif self.user is not None:
            # User is logged in and already registered, do not re-register:
            self.redirect('/')

        user_id = self.current_user.user_id()
        email = self.current_user.email()

        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')

        if email is None or re.match(r"^\s*$", email):
            email = self.request.get('email')

        User.add_or_get_user(user_id=user_id, email=email, first_name=first_name, last_name=last_name)

        self.redirect('/')
