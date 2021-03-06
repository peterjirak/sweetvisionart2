import json
import time

from google.appengine.api import users
from models.visitor import Visitor
from handlers.base import BasePageHandler


class VisitorHandler(BasePageHandler):
    def get(self):
        # Only let an admin user retrieve the information about visitors:
        if not users.is_current_user_admin():
            self.response.headers['Content-Type'] = 'application/json'
            self.response.status = '401 Unauthorized'
            self.response.write(json.dumps({'status': 401,
                                            'error': 'Unauthorized'}))
            return

        visitors_from_datastore = Visitor.get_visitors()
        visitors = []
        for visitor_instance in visitors_from_datastore:
            visitor = dict()
            visitor['google_user_id'] = None
            if visitor_instance.google_user_id is not None:
                visitor['google_user_id'] = str(visitor_instance.google_user_id)
            visitor['email'] = None
            if visitor_instance.email is not None:
                visitor['email'] = str(visitor_instance.email)
            visitor['auth_domain'] = None
            if visitor_instance.auth_domain is not None:
                visitor['auth_domain'] = str(visitor_instance.auth_domain)
            visitor['nickname'] = None
            if visitor_instance.nickname is not None:
                visitor['nickname'] = str(visitor_instance.nickname)
            if visitor_instance.is_admin:
                visitor['is_admin'] = True
            else:
                visitor['is_admin'] = False
            visitor['google_user_object'] = None
            if visitor_instance.google_user_object is not None:
                visitor['google_user_object'] = str(visitor_instance.google_user_object)
            visitors.append(visitor)
            visitor['created_at'] = None
            if visitor_instance.created_at is not None:
                created_at_epoch_time = time.mktime(visitor_instance.created_at.timetuple())
                visitor['created_at'] = created_at_epoch_time

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps({'visitors': visitors}))
