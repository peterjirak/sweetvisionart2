import re
import uuid

from google.appengine.ext import ndb


class User(ndb.Model):
    # Have an application_user_id, use the application_user_id to identify the user within the application
    # the application user_id can be used in URLs to identify the application user, like his or her profile.
    application_user_id = ndb.StringProperty(required=True)

    # Store the user's Google user ID to associate the user's Google account with the application. But do not
    # user the user's Google user ID in URLs like the link to the user's profile. Exposing the user's Google
    # user ID, allows activity in one Google App Engine application to be associated with activity in another
    # Google App Engine application (this reduces a user's privacy). It also allows another Google App Engine
    # Application to register the user using his or her Google user ID without his or her permission. Use
    # Google user IDs but do not expose them externally like in URLs.
    google_user_id = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    created_at = ndb.DateTimeProperty(required=True, auto_now_add=True)

    @classmethod
    def get_user_by_google_user_id(cls, google_user_id):
        if google_user_id is not None:
            google_user_id = str(google_user_id)

        if google_user_id is None or re.match(r"^\s*$", google_user_id):
            raise ValueError("User.get_user_by_google_id requires a google_user_id.")

        google_user_id = google_user_id.strip()
        key = ndb.Key('User', google_user_id)
        qry = cls.query(ancestor=key)

        user_inst = qry.get()

        return user_inst

    @classmethod
    def add_or_get_user(cls, google_user_id, email, first_name, last_name):
        if google_user_id is not None:
            google_user_id = str(google_user_id)

        if google_user_id is None or re.match(r"^\s*$", google_user_id):
            raise ValueError("user_id is required for a User")

        if email is None or re.match(r"^\s*$", email):
            raise ValueError("email is required for a User")
        elif first_name is None or re.match(r"^\s*$", first_name):
            raise ValueError("first_name is required for a User")
        elif last_name is None or re.match(r"^\s*$", last_name):
            raise ValueError("last_name is required for a User")

        google_user_id = google_user_id.strip()
        email = email.strip()
        first_name = first_name.strip()
        last_name = last_name.strip()

        user_inst = User.get_user_by_google_user_id(google_user_id)

        if user_inst is not None:
            if user_inst.email != email:
                raise ValueError("A user exists for the user_id %s but the email is '%s', not '%s'." %
                                 (google_user_id, user_inst.email, email))
            elif user_inst.first_name != first_name:
                raise ValueError(("A user exists for the user_id %s with the email '%s', but the first_name is '%s', " +
                                  "not '%s'.") % (google_user_id, email, user_inst.first_name, first_name))
            elif user_inst.last_name != last_name:
                raise ValueError(("A user exists for the user_id %s with the email '%s' and first_name '%s', but the " +
                                  "last_name is '%s', not '%s'.") % (google_user_id, email, first_name, user_inst.last_name,
                                                                     last_name))
            else:
                return user_inst

        qry = cls.query(User.email == email)

        user_inst = qry.get()

        if user_inst:
            raise ValueError("A user exists with the email '%s', but its user_id is '%s', not '%s'." %
                             (email, user_inst.user_id, google_user_id))

        application_user_id = str(uuid.uuid4())
        key = ndb.Key('User', google_user_id)

        user_inst = User(parent=key, application_user_id=application_user_id, google_user_id=google_user_id,
                        email=email, first_name=first_name, last_name=last_name)
        user_inst.put()

        return user_inst
