import re
import jsonpickle
from google.appengine.ext import ndb

# import sys
# import json as JSON
# sys.modules['simplejson'] = JSON

import jsonpickle


class Visitor(ndb.Model):
    google_user_id = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
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
    def add_or_get_visitor(cls, google_user_object):
        google_user_id = google_user_object.user_id()
        if google_user_id is None or re.match(r"^\s*$", str(google_user_id)):
            raise ValueError("add_or_get_user called with an object that does not have a valid user_id")

        visitor_inst = Visitor.get_visitor_by_google_user_id(google_user_id)
        if visitor_inst is not None:
            return visitor_inst

        email = google_user_object.email()
        key = ndb.Key('Visitor', google_user_id)

        visitor_inst = Visitor(parent=key)
        visitor_inst.google_user_id = google_user_id
        if email is not None and not re.match(r"^\s*$", str(email)):
            visitor_inst.email = email
        visitor_inst.google_user_object = jsonpickle.encode(google_user_object)

        visitor_inst.put()

        return visitor_inst

    @classmethod
    def get_visitors(cls):
        qry = cls.query().order(-cls.created_at)
        visitors = qry.fetch()

        return visitors