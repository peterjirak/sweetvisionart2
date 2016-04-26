from google.appengine.ext import ndb
from google.appengine.api import images

import webapp2
from handlers.base import BasePageHandler

from models.art import Art


class ImageHandler(BasePageHandler):
    def get(self, id, flag=None):
        art_for_image = Art()
        key = ndb.Key(urlsafe=id)
        art_for_image = art_for_image.get_art_by_id(key.id())
        scaled = images.resize(art_for_image.image, height=300)

        if art_for_image:
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(scaled)
