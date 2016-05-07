import re

from models.profile import Profile
from handlers.base_registered_user_handler import BaseRegisteredUserPageHandler
from exceptions import UnauthorizedException, NotRegisteredException


class EditProfileHandler(BaseRegisteredUserPageHandler):
    def get(self):
        if self.redirected:
            # The call was redirected in the __init__ -- do not do anything in this
            # handler -- just return
            return

        if not self.google_user:
            # The __init__ definitions in the base classes should redirect to authentication, so this should never
            # happen. However, we include this check if somehow this get handler is invoked but the user is not
            # authenticated
            raise UnauthorizedException("/edit_profile invoked but user has not been authenticated. " +
                                        "Unable to handle request.")

        elif not self.application_user:
            # The __init__ definitions in the base classes should redirect to /register_user, so this should never
            # happen. However, we include this check if somehow this get handler is invoked but the user is
            # not registered.
            raise NotRegisteredException("/edit_profile invoked but the user has not registered. " +
                                         "Unable to handle request.")

        template = self.get_template('templates/edit_profile.html')

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
            if self.request.path is not None and not re.match(r"r^\s*$", self.request.path):
                continue_to = self.request.path
        if continue_to is None or re.match(r"^\s*$", continue_to):
            continue_to = '/edit_profile'
        self.template_values['after_editing_profile_continue_to'] = continue_to

        application_user = self.application_user

        if application_user.first_name is not None and \
           not re.match(r"^\s*$", application_user.first_name):
            self.template_values['first_name'] = application_user.first_name

        if application_user.middle_name is not None and \
           not re.match(r"^\s*$", application_user.middle_name):
            self.template_values['middle_name'] = application_user.middle_name

        if application_user.last_name is not None and \
           not re.match(r"^\s*$", application_user.last_name):
            self.template_values['last_name'] = application_user.last_name

        google_user = self.google_user
        email = google_user.email()

        if email and not re.match(r"^\s*$", email):
            self.template_values['email'] = email

        application_user_id = application_user.application_user_id
        profile_obj = Profile.get_profile_by_application_user_id(application_user_id)

        if profile_obj is not None:
            profile_unique_display_name = profile_obj.profile_unique_display_name
            if profile_unique_display_name is not None and not re.match(r"^\s*", profile_unique_display_name):
                self.template_values['profile_unique_display_name'] = profile_unique_display_name
            bio = profile_obj.bio
            if bio is not None and not re.match(r"^\s*$", bio):
                self.template_values['bio'] = bio

        self.response.write(template.render(self.template_values))
