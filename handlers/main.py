from google.appengine.api import users

from handlers.base_registered_user_handler import BaseRegisteredUserPageHandler

from models.art import Art
from models.profile import Profile


class MainHandler(BaseRegisteredUserPageHandler):
    def get(self):
        art_item = Art()
        art_list = art_item.get_art()
        self.template_values['art_list'] = art_list

        template = self.get_template('templates/index.html')
        self.response.write(template.render(self.template_values))
