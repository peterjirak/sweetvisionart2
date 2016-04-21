#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

from google.appengine.api import users
import webapp2

import jinja2

from models.art import Art
from models.profile import Profile

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)


class _PageHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super(_PageHandler, self).__init__(request, response)
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


class MainHandler(_PageHandler):
    def get(self):
        if users.get_current_user():
            user_id = users.get_current_user().user_id()
            user_profile = Profile(user_id=user_id)

        art_item = Art()
        art_list = art_item.get_art()
        self.template_values['art_list'] = art_list

        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(self.template_values))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
