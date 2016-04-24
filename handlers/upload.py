import json

from google.appengine.api import users
from google.appengine.api import images

from handlers.base import BasePageHandler

from models.art import Art


class UploadHandler(BasePageHandler):
    def get(self):
        if not users.get_current_user():
            return self.redirect("/register_user")
        template = self.get_template('templates/file_upload.html')
        self.response.write(template.render(self.template_values))

    def post(self):
        # TODO : Handle post request from non-logged in user (Respond with an HTTP Error code of 403 -- forbidden)
        # TODO : Make adding an image to the Google datastore strongly consistent
        # TODO : Create a URL for the image detail page -- add that URL to the response in the url field
        # TODO : Add support for image thumbnails.
        new_art = Art()
        if users.get_current_user():
            new_art.user_id = users.get_current_user().user_id()
        new_art.title = self.request.get('title[]')
        new_art.description = self.request.get('description[]')
        filename = self.request.POST.get('userfile').filename
        art_image = self.request.get('userfile')
        file_size = len(art_image)
        art_image = images.resize(art_image, 600, 600)
        new_art.image = art_image
        new_art.put()

        response_body = {
            "files": [ {
                "name": filename,
                "size": file_size
            } ]
        }

        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.write(json.dumps(response_body))
