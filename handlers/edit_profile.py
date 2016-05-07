import re
import urllib

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
            if profile_unique_display_name is not None and not re.match(r"^\s*$", profile_unique_display_name):
                self.template_values['profile_unique_display_name'] = profile_unique_display_name
            bio = profile_obj.bio
            if bio is not None and not re.match(r"^\s*$", bio):
                self.template_values['bio'] = bio
            self.template_values['is_update'] = True

        self.response.write(template.render(self.template_values))

    def post(self):
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

        continue_to = self.request.get('after_editing_profile_continue_to')
        if continue_to is None or re.match(r"^\s*$", continue_to):
            continue_to = '/'
        continue_to = str(continue_to)

        google_user = self.google_user
        application_user = self.application_user

        first_name = self.request.get('first_name')
        middle_name = self.request.get('middle_name')
        last_name = self.request.get('last_name')

        if first_name is not None:
            first_name = first_name.strip()

        if last_name is not None:
            last_name = last_name.strip()

        if middle_name is not None:
            middle_name = middle_name.strip()

        application_user_changed = False
        feedback = None
        feedback_status = None

        if first_name is not None and not re.match(r"^\s*$", first_name):
            if first_name != application_user.first_name:
                application_user.first_name = first_name
                application_user_changed = True

        if last_name is not None and not re.match(r"^\s*$", last_name):
            if last_name != application_user.last_name:
                application_user.last_name = last_name
                application_user_changed = True

        if middle_name is None or middle_name == '':
            if application_user.middle_name is not None and not re.match(r"^\s*$", application_user.middle_name):
                application_user.middle_name = None
                application_user_changed = True
        else:
            if application_user.middle_name is None or re.match(r"^\s*$", application_user.middle_name):
                application_user.middle_name = middle_name
                application_user_changed = True
            elif application_user.middle_name != application_user.middle_name:
                application_user.middle_name = middle_name
                application_user_changed = True

        if application_user_changed:
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

                edit_profile_url = self.request.application_url
                if not re.match(r"^.*$", edit_profile_url):
                    edit_profile_url += '/'
                edit_profile_url += 'edit_profile'

                feedback = urllib.quote(feedback, safe='')
                feedback_status = urllib.quote(feedback_status, safe='')

                return self.redirect(edit_profile_url + '?feedback=' + feedback + '&feedback_status=' + feedback_status)

        bio = self.request.get('bio')
        if bio is not None:
            bio = bio.strip()
            if bio == '' or re.match(r"^\s*$", bio):
                bio = None

        application_user_id = application_user.application_user_id
        profile_unique_display_name = self.request.get('profile_unique_display_name')
        profile_unique_display_name = profile_unique_display_name.strip()
        profile_obj_for_user = Profile.get_profile_by_application_user_id(application_user_id)
        profile_obj_for_profile_name = Profile.get_profile_by_profile_unique_name(profile_unique_display_name)
        if profile_obj_for_profile_name is not None:
            # There is already a profile for the given profile unique display name:
            if profile_obj_for_profile_name.application_user_id != application_user_id:
                # The profile that already exists is not for this user but is for another user:
                feedback = "Cannot setup your profile, the profile name '%s' is already in use." % \
                           profile_unique_display_name
                feedback_status = 'Failure'

                edit_profile_url = self.request.application_url
                if not re.match(r"^.*$", edit_profile_url):
                    edit_profile_url += '/'
                edit_profile_url += 'edit_profile'

                feedback = urllib.quote(feedback, safe='')
                feedback_status = urllib.quote(feedback_status, safe='')

                return self.redirect(edit_profile_url + '?feedback=' + feedback + '&feedback_status=' + feedback_status)
            else:
                # The profile already exists and is for this user:
                profile_changed = False
                if bio is None and profile_obj_for_profile_name.bio is not None:
                    profile_obj_for_profile_name.bio = None
                    profile_changed = True
                if profile_changed:
                    update_success = True
                    try:
                        profile_obj_for_profile_name.put()
                    except:
                        update_success = False
                    if update_success:
                        feedback = 'Successfully updated your profile.'
                        feedback_status = 'Success'
                    else:
                        feedback = 'Attempt to update your profile failed.'
                        feedback_status = 'Failure'
                elif feedback is None:
                    feedback = 'Your profile information is unchanged.'
                    feedback_status = 'No_Change'
                edit_profile_url = self.request.application_url
                if not re.match(r"^.*$", edit_profile_url):
                    edit_profile_url += '/'
                edit_profile_url += 'edit_profile'

                feedback = urllib.quote(feedback, safe='')
                feedback_status = urllib.quote(feedback_status, safe='')

                return self.redirect(edit_profile_url + '?feedback=' + feedback + '&feedback_status=' + feedback_status)
        elif profile_obj_for_user is not None:
            # The user has a profile object
            profile_unique_name = Profile.get_profile_unique_name_from_profile_display_name(profile_unique_display_name)
            if profile_unique_name != profile_obj_for_user.profile_unique_name:
                # Request to change the profile unique name:
                # First, delete the existing profile object:
                delete_sucess = True
                try:
                    profile_obj_for_user.key.delete()
                except:
                    delete_sucess = False
                if not delete_sucess:
                    feedback = 'Attempt to update your profile failed.'
                    feedback_status = 'Failure'
                else:
                    # Next, create a new profile object using the new profile unique name:
                    new_profile_success = True
                    try:
                        new_profile_obj = Profile.add_profile(profile_unique_display_name, application_user_id, bio=bio)
                    except:
                        new_profile_success = False
                    if new_profile_success:
                        feedback = 'Successfully updated your profile.'
                        feedback_status = 'Success'
                    else:
                        feedback = 'Attempt to update your profile failed.'
                        feedback_status = 'Failure'
            else:
                feedback = 'Your profile information is unchanged.'
                feedback_status = 'No_Change'

            edit_profile_url = self.request.application_url
            if not re.match(r"^.*$", edit_profile_url):
                edit_profile_url += '/'
            edit_profile_url += 'edit_profile'

            feedback = urllib.quote(feedback, safe='')
            feedback_status = urllib.quote(feedback_status, safe='')

            return self.redirect(edit_profile_url + '?feedback=' + feedback + '&feedback_status=' + feedback_status)
        else:
            # Create a new profile for this user:
            new_profile_success = True
            try:
                new_profile_obj = Profile.add_profile(profile_unique_display_name, application_user_id, bio=bio)
            except:
                new_profile_success = False
            if new_profile_success:
                feedback = 'Successfully created your profile.'
                feedback_status = 'Success'
            else:
                feedback = 'Attempt to create your profile failed.'
                feedback_status = 'Failure'

            edit_profile_url = self.request.application_url
            if not re.match(r"^.*$", edit_profile_url):
                edit_profile_url += '/'
            edit_profile_url += 'edit_profile'

            feedback = urllib.quote(feedback, safe='')
            feedback_status = urllib.quote(feedback_status, safe='')

            return self.redirect(edit_profile_url + '?feedback=' + feedback + '&feedback_status=' + feedback_status)
