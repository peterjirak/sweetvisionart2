import re
import os

from google.appengine.api import users

import webapp2

import jinja2

from models.profile import Profile


class BasePageHandler(webapp2.RequestHandler):
    __JINJA_ENVIRONMENT = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/..'),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True)

    def __init__(self, request=None, response=None):
        super(BasePageHandler, self).__init__(request, response)
        self.template_values = {}
        self.user = users.get_current_user()
        if self.user:
            self.template_values['user_name'] = self.user.nickname()
            self.profile = Profile.query(Profile.user_id == self.user.user_id()).get()
            # self.template_values['profile_unique_name'] = self.profile.profile_unique_name
            self.LogInOutURL = users.create_logout_url('/')
        else:
            self.LogInOutURL = users.create_login_url('/')

        self.template_values['LogInOutURL'] = self.LogInOutURL

    def get_template(self, template_file):
        if template_file is None or re.match(r"^\s*$", template_file):
            raise ValueError('get_template called without a valid template_file')

        template = self.__JINJA_ENVIRONMENT.get_template(template_file)
        return template
