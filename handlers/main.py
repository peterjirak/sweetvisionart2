import re
from handlers.base import BasePageHandler

from models.art import Art
from models.user import User
from models.profile import Profile

# TODO : Support paging


class MainHandler(BasePageHandler):
    def get(self):
        application_url = self.request.application_url
        if not re.match(r"^.*/$", application_url):
            application_url += '/'
        art_objs = Art.get_art()
        art_list = list()
        artists_by_app_user_id = dict()
        artists_looked_up_by_app_user_id = dict()
        profiles_by_app_user_id = dict()
        profiles_looked_up_by_app_user_id = dict()
        for art_obj in art_objs:
            art = dict()
            art['art_obj'] = art_obj
            app_user_id = art_obj.application_user_id
            if app_user_id is not None:
                user_obj = artists_by_app_user_id.get(app_user_id)
                if user_obj is None and not artists_looked_up_by_app_user_id.get(app_user_id):
                    artists_looked_up_by_app_user_id[app_user_id] = True
                    user_obj = User.get_user_by_application_user_id(app_user_id)
                    if user_obj is not None:
                        artists_by_app_user_id[app_user_id] = user_obj
                profile_obj = profiles_by_app_user_id.get(app_user_id)
                if profile_obj is None and not profiles_looked_up_by_app_user_id.get(app_user_id):
                    profiles_looked_up_by_app_user_id[app_user_id] = True
                    profile_obj = Profile.get_profile_by_application_user_id(app_user_id)
                    if profile_obj is not None:
                        profiles_by_app_user_id[app_user_id] = profile_obj

            artist_nickname = None
            if profile_obj is not None:
                artist_nickname = profile_obj.profile_unique_name
                art['artist_nickname'] = artist_nickname

            if user_obj is not None:
                art['artist_name'] = user_obj.first_name + ' ' + user_obj.last_name
                if artist_nickname is not None:
                    art['artist_url'] = application_url + artist_nickname
                else:
                    art['artist_url'] = application_url + app_user_id
            art_list.append(art)

        self.template_values['art_list'] = art_list

        template = self.get_template('templates/index.html')
        self.response.write(template.render(self.template_values))
