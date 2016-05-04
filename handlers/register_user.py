import re
import urllib

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

        feedback = self.request.get('feedback')
        feedback_status = self.request.get('feedback_status')

        if feedback is not None and not re.match(r"^\s*$", feedback):
            feedback = feedback.strip()
            self.template_values['feedback'] = feedback
            if feedback_status is None or re.match(r"^\s*$", feedback_status):
                feedback_status = 'No_Change'
            feedback_status = feedback_status.strip()
            self.template_values['feedback_status'] = feedback_status

        continue_to = self.request.get('continue')
        if continue_to is None or re.match(r"^\s*$", continue_to):
            continue_to = '/'

        self.template_values['is_update'] = False
        if self.application_user:
            # The user has already registered -- load the template values with the existing
            # values for the user to permit the user to change his or her registration information:
            self.template_values['is_update'] = True
            if self.request.path is not None and not re.match(r"r^\s*$", self.request.path):
                continue_to = self.request.path
            else:
                continue_to = '/register_user'
            if self.application_user.first_name is not None and \
               not re.match(r"^\s*$", self.application_user.first_name):
                self.template_values['first_name'] = self.application_user.first_name

            if self.application_user.first_name is not None and \
               not re.match(r"^\s*$", self.application_user.first_name):
                self.template_values['middle_name'] = self.application_user.middle_name

            if self.application_user.last_name is not None and \
               not re.match(r"^\s*$", self.application_user.last_name):
                self.template_values['last_name'] = self.application_user.last_name

        self.template_values['after_registration_continue_to'] = continue_to

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

        google_user = self.google_user
        if not self.logged_in or not google_user:
            # Must login using Google Auth before registering:
            self.redirect(users.create_login_url(continue_to))
            return # return after redirect

        google_user_id = google_user.user_id()
        email = google_user.email()
        first_name = self.request.get('first_name')
        middle_name = self.request.get('middle_name')
        last_name = self.request.get('last_name')

        if email is None or re.match(r"^\s*$", email):
            email = self.request.get('email')

        if first_name is not None:
            first_name = first_name.strip()

        if last_name is not None:
            last_name = last_name.strip()

        if middle_name is not None:
            middle_name = middle_name.strip()

        if email is not None:
            email = email.strip()

        application_user = self.application_user

        if application_user is not None:
            # POST request is to update the registration of an existing user:
            has_changed = False
            if first_name is not None and not re.match(r"^\s*$", first_name):
                if first_name != application_user.first_name:
                    application_user.first_name = first_name
                    has_changed = True

            if last_name is not None and not re.match(r"^\s*$", last_name):
                if last_name != application_user.last_name:
                    application_user.last_name = last_name
                    has_changed = True

            if middle_name is None or middle_name == '':
                if application_user.middle_name is not None and not re.match(r"^\s*$", application_user.middle_name):
                    application_user.middle_name = None
                    has_changed = True
            else:
                if application_user.middle_name is None or re.match(r"^\s*$", application_user.middle_name):
                    application_user.middle_name = middle_name
                    has_changed = True
                elif application_user.middle_name != application_user.middle_name:
                    application_user.middle_name = middle_name
                    has_changed = True

            if has_changed:
                update_success = True
                try:
                    application_user.put()
                except:
                    update_success = False
                if update_success:
                    feedback = 'Successfully updated your registration.'
                    feedback_status = 'Success'
                else:
                    feedback = 'Attempt to update your registration failed.'
                    feedback_status = 'Failure'
            else:
                feedback = 'Your registration information is unchanged.'
                feedback_status = 'No_Change'
        else:
            # POST request is to register the user:
            create_success = True
            try:
                application_user = User.add_or_get_user(google_user_id=google_user_id, email=email,
                                                        first_name=first_name, middle_name=middle_name,
                                                        last_name=last_name)
            except:
                create_success = False

            if create_success and application_user is None:
                create_success = False

            if create_success:
                feedback = 'You have been registered.'
                feedback_status = 'Success'
            else:
                feedback = 'Registration failed.'
                feedback_status = 'Failure'

        feedback = urllib.quote(feedback, safe='')
        feedback_status = urllib.quote(feedback_status, safe='')

        return self.redirect(continue_to + '?feedback=' + feedback + '&feedback_status=' + feedback_status)
