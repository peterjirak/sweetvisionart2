import re

from google.appengine.ext import ndb
from google.appengine.api import users

import jsonpickle


class Visitor(ndb.Model):
    google_user_id = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    nickname = ndb.StringProperty()
    is_admin = ndb.BooleanProperty(default=False)
    auth_domain = ndb.StringProperty()
    google_user_object = ndb.BlobProperty(required=True)
    created_at = ndb.DateTimeProperty(required=True, auto_now_add=True)

    @classmethod
    def get_visitor_by_google_user_id(cls, google_user_id):
        if google_user_id is not None:
            google_user_id = str(google_user_id)

        if google_user_id is None or re.match(r"^\s*$", google_user_id):
            raise ValueError("User.get_user_by_google_id requires a google_user_id.")

        google_user_id = google_user_id.strip()
        key = ndb.Key('Visitor', google_user_id)
        qry = cls.query(ancestor=key)

        visitor_inst = qry.get()

        return visitor_inst

    @classmethod
    def add_or_get_current_user_as_visitor(cls):
        current_user = users.get_current_user()
        if current_user is None:
            return None

        google_user_id = current_user.user_id()

        if google_user_id is None or re.match(r"^\s*$", str(google_user_id)):
            raise ValueError("A valid user_id add_or_get_current_user called with an object that does not have a valid user_id")

        visitor_inst = Visitor.get_visitor_by_google_user_id(google_user_id)
        if visitor_inst is not None:
            return visitor_inst

        email = current_user.email()
        is_admin = users.is_current_user_admin()
        auth_domain = current_user.auth_domain()
        nickname = current_user.nickname()
        key = ndb.Key('Visitor', google_user_id)

        visitor_inst = Visitor(parent=key)
        visitor_inst.google_user_id = google_user_id
        visitor_inst.is_admin = is_admin
        if email is not None and not re.match(r"^\s*$", str(email)):
            visitor_inst.email = email
        if auth_domain is not None and not re.match(r"^\s*$", str(auth_domain)):
            visitor_inst.auth_domain = auth_domain
        if nickname is not None and re.match(r"^\s*$", str(nickname)):
            visitor_inst.nickname = nickname

        visitor_inst.google_user_object = jsonpickle.encode(current_user)

        visitor_inst.put()

        return visitor_inst

    @classmethod
    def get_visitors(cls):
        qry = cls.query().order(-cls.created_at)
        visitors = qry.fetch()

        return visitors