from handlers.base import BasePageHandler

from models.art import Art


class MainHandler(BasePageHandler):
    def get(self):
        art_item = Art()
        art_list = art_item.get_art()
        self.template_values['art_list'] = art_list

        template = self.get_template('templates/index.html')
        self.response.write(template.render(self.template_values))
