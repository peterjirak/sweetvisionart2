import re

from google.appengine.api import users

from exceptions import UnauthorizedException
from handlers.base_authenticated_user_handler import BaseAuthenticatedUserPageHandler
from models.user import User


class RegisterUserHandler(BaseAuthenticatedUserPageHandler):
    def get(self):
        if self.redirected:
            # The call was redirected in the __init__ -- do not do anything in this
            # handler -- just return
            return

        if not self.google_user:
            # The __init__ definitions in the base classes should redirect to authentication, so this should never
            # happen. However, we include this check if somehow this get handler is invoked but the user is not
            # authenticated
            raise UnauthorizedException("/register_user invoked but user has not been authenticated. " +
                                        "Unable to handle request.")

        continue_to = self.request.get('continue')
        if continue_to is None or re.match(r"^\s*$", continue_to):
            continue_to = '/'

        if self.application_user:
            # The current user is already registered -- no need to display the registration form
            return self.redirect(continue_to)

        self.template_values['after_registration_continue_to'] = continue_to

        if self.application_user is not None:
            # User is logged in and already registered, do not re-register:
            return self.redirect('/')

        # Get email from Google Auth user object if available:
        if self.google_user.email():
            email = self.google_user.email()
        else:
            email = None

        self.template_values['email'] = email

        template = self.get_template('templates/register_user.html')
        self.response.write(template.render(self.template_values))

    def post(self):
        if self.redirected:
            # The call was redirected in the __init__ -- do not do anything in this
            # handler -- just return
            return

        continue_to = self.request.get('after_registration_continue_to')
        if continue_to is None or re.match(r"^\s*$", continue_to):
            continue_to = '/'
        continue_to = str(continue_to)

        if not self.logged_in:
            # Must login using Google Auth before registering:
            self.redirect(users.create_login_url(continue_to))
        elif self.application_user is not None:
            # User is logged in and already registered, do not re-register:
            self.redirect(continue_to)

        google_user_id = self.google_user.user_id()
        email = self.google_user.email()

        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')

        if email is None or re.match(r"^\s*$", email):
            email = self.request.get('email')

        User.add_or_get_user(google_user_id=google_user_id, email=email, first_name=first_name, last_name=last_name)

        return self.redirect(continue_to)
