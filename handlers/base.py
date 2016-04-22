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
        self.user = None
        self.current_user = None
        current_user = users.get_current_user()
        if current_user:
            self.current_user = current_user
            self.logged_in = True
            user_id = current_user.user_id()
            user = User.get_user_by_id(user_id)
            if user:
                self.user = user
                display_user_name = user.first_name + ' ' + user.last_name
                self.template_values['display_user_name'] = display_user_name
            else:
                if current_user.email():
                    display_user_name = current_user.email()
                elif current_user.nickname():
                    display_user_name = current_user.nickname()
                else:
                    display_user_name = current_user.user_id()

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
