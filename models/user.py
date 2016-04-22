import re
from google.appengine.ext import ndb


class User(ndb.Model):
    user_id = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty(required=True)
    created_at = ndb.DateTimeProperty(required=True, auto_now_add=True)

    @classmethod
    def get_user_by_id(cls, user_id):
        if user_id is not None:
            user_id = str(user_id)

        if user_id is None or re.match(r"^\s*$", user_id):
            raise ValueError("User.get_user_by_id requires a user_id.")

        user_id = user_id.strip()
        key = ndb.Key('User', user_id)
        qry = cls.query(ancestor=key)

        user_inst = qry.get()

        return user_inst

    @classmethod
    def add_or_get_user(cls, user_id, email, first_name, last_name):
        if user_id is not None:
            user_id = str(user_id)

        if user_id is None or re.match(r"^\s*$", user_id):
            raise ValueError("user_id is required for a User")

        if email is None or re.match(r"^\s*$", email):
            raise ValueError("email is required for a User")
        elif first_name is None or re.match(r"^\s*$", first_name):
            raise ValueError("first_name is required for a User")
        elif last_name is None or re.match(r"^\s*$", last_name):
            raise ValueError("last_name is required for a User")

        user_id = user_id.strip()
        email = email.strip()
        first_name = first_name.strip()
        last_name = last_name.strip()

        user_inst = User.get_user_by_id(user_id)

        if user_inst is not None:
            if user_inst.email != email:
                raise ValueError("A user exists for the user_id %s but the email is '%s', not '%s'." %
                                 (user_id, user_inst.email, email))
            elif user_inst.first_name != first_name:
                raise ValueError(("A user exists for the user_id %s with the email '%s', but the first_name is '%s', " +
                                  "not '%s'.") % (user_id, email, user_inst.first_name, first_name))
            elif user_inst.last_name != last_name:
                raise ValueError(("A user exists for the user_id %s with the email '%s' and first_name '%s', but the " +
                                  "last_name is '%s', not '%s'.") % (user_id, email, first_name, user_inst.last_name,
                                                                     last_name))
            else:
                return user_inst

        qry = cls.query(User.email == email)

        user_inst = qry.get()

        if user_inst:
            raise ValueError("A user exists with the email '%s', but its user_id is '%s', not '%s'." %
                             (email, user_inst.user_id, user_id))

        key = ndb.Key('User', user_id)

        user_inst = User(parent=key, user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user_inst.put()

        return user_inst
