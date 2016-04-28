import re

from models.user import User
from models.profile import Profile
from models.art import Art
from handlers.base import BasePageHandler

# TODO : Support paging


class ArtistPageHandler(BasePageHandler):
    def get(self, artist_id):
        # artist_id may be a profile_unique_name or an application_user_id
        profile_obj = Profile.get_profile_by_profile_unique_name(artist_id)
        if profile_obj is not None:
            application_user_id = profile_obj.application_user_id
            user_obj = User.get_user_by_application_user_id(application_user_id)
            if user_obj is None:
                # TODO : All profiles should have a user associated with them. Log or handle the event where there is no User associated with a profile.
                # There is no user associated with the profile!
                pass
        else:
            user_obj = User.get_user_by_application_user_id(artist_id)
            if user_obj is not None:
                profile_obj = Profile.get_profile_by_application_user_id(user_obj.application_user_id)

        if user_obj is not None:
            self.template_values['user_exists'] = True
            self.template_values['artist_name'] = user_obj.first_name + ' ' + user_obj.last_name
            if profile_obj is not None:
                self.template_values['profile_unique_name'] = profile_obj.profile_unique_name
                if profile_obj.bio is not None and not re.match(r"^\s*$", profile_obj.bio):
                    self.template_values['profile_bio'] = profile_obj.bio
                if profile_obj.profile_picture is not None:
                    self.template_values['profile_picture'] = profile_obj.profile_picture
            self.template_values['art_list'] = Art.get_art(user_obj.application_user_id)
            self.template_values['artist_image_count'] = len(self.template_values['art_list'])
        else:
            self.template_values['user_exists'] = False

        template = self.get_template('templates/artist_content.html')
        self.response.write(template.render(self.template_values))
