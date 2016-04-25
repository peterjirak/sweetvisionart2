import re
import os

from google.appengine.api import users

import webapp2

import jinja2

from models.user import User


class BasePageHandler(webapp2.RequestHandler):
    __JINJA_ENVIRONMENT = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/..'),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True)

    def __init__(self, request=None, response=None):
        super(BasePageHandler, self).__init__(request, response)
        self.LogInOutURL = users.create_logout_url('/')
        self.template_values = {}
        self.application_user = None
        self.google_user = None
        google_user = users.get_current_user()
        if google_user:
            self.google_user = google_user
            self.logged_in = True
            google_user_id = google_user.user_id()
            application_user = User.get_user_by_google_user_id(google_user_id)
            if application_user:
                self.application_user = application_user
                display_user_name = application_user.first_name + ' ' + application_user.last_name
                self.template_values['display_user_name'] = display_user_name
            else:
                if google_user.email():
                    display_user_name = google_user.email()
                elif google_user.nickname():
                    display_user_name = google_user.nickname()
                else:
                    display_user_name = 'Sweet Vision User'

                self.template_values['display_user_name'] = display_user_name
        else:
            self.logged_in = False
            self.LogInOutURL = users.create_login_url('/')

        self.template_values['LogInOutURL'] = self.LogInOutURL

    def get_template(self, template_file):
        if template_file is None or re.match(r"^\s*$", template_file):
            raise ValueError('get_template called without a valid template_file')

        template = self.__JINJA_ENVIRONMENT.get_template(template_file)
        return template
