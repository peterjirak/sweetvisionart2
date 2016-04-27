import re
import json

from google.appengine.api import users
from google.appengine.api import images

from handlers.base_registered_user_handler import BaseRegisteredUserPageHandler

from models.art import Art
from models.user import User


class UploadHandler(BaseRegisteredUserPageHandler):
    def __init__(self, request=None, response=None):
        if request is not None:
            method = request.method
            if method == 'POST':
                self.no_redirect = True

        super(UploadHandler, self).__init__(request, response)

    def get(self):
        if self.redirected:
            # The call was redirected in the __init__ -- do not do anything in this
            # handler -- just return
            return

        template = self.get_template('templates/file_upload.html')
        self.response.write(template.render(self.template_values))

    def post(self):
        file_response = {}

        title = self.request.get('title[]')
        if title is not None:
            title = title.strip()
        description = self.request.get('description[]')
        if description is not None:
            description = description.strip()
        filename = self.request.POST.get('userfile').filename
        art_image = self.request.get('userfile')
        file_size = len(art_image)

        file_response['name'] = filename
        file_response['size'] = file_size
        error = None

        application_user_id = None
        google_user = users.get_current_user()

        if not google_user:
            error = 'You must login before you can POST an image to /upload'
        else:
            google_user_id = google_user.user_id()
            if not google_user_id:
                error = 'You must login before you can POST an image to /upload'
            else:
                application_user = User.get_user_by_google_user_id(google_user_id)
                if not application_user:
                    error = 'You must register before you can POST an image to /upload'
                else:
                    application_user_id = application_user.application_user_id
                    if not application_user_id:
                        error = 'You must register before you can POST an image to /upload'

        if error is not None:
            file_response['error'] = error
            self.response.status = '401 Unauthorized'
        else:
            new_art = Art()
            new_art.title = title
            new_art.description = description
            new_art.application_user_id = application_user_id
            new_art.image = images.resize(art_image, 600, 600)
            new_key = new_art.put()

            new_image_url = self.request.application_url
            if not re.match(r"^.*/$", new_image_url):
                new_image_url += '/'
            new_image_url += 'image/' + new_key.urlsafe()

            file_response['url'] = new_image_url
            file_response['thumbnail_url'] = new_image_url

        response_body = {
            "files": [file_response]
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(response_body))
