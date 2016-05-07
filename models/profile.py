import re

from google.appengine.ext import ndb
from exceptions import UniquenessConstraintViolatedException


class Profile(ndb.Model):
    application_user_id = ndb.StringProperty(required=True)
    profile_unique_name = ndb.StringProperty(required=True)
    profile_unique_display_name = ndb.StringProperty(required=True)
    bio = ndb.TextProperty(required=False)
    profile_picture = ndb.BlobProperty(required=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_profile_unique_name_from_profile_display_name(cls, profile_display_name):
        if profile_display_name is None or not re.search(r"[A-Za-z0-9]", profile_display_name):
            raise ValueError("Profile.get_profile_unique_name_from_profile_display_name called " +
                             "without a valid profile_display_name")
        profile_display_name = re.sub(r"[^A-Za-z0-9]", '', profile_display_name)
        profile_display_name = profile_display_name.lower()

        return profile_display_name

    @classmethod
    def get_profile_by_profile_unique_name(cls, profile_unique_name):
        if profile_unique_name is not None:
            profile_unique_name = str(profile_unique_name)

        if profile_unique_name is None or re.match(r"^\s*$", profile_unique_name):
            raise ValueError("Profile.get_profile_by_unique_name requires a profile name.")

        profile_unique_name = Profile.get_profile_unique_name_from_profile_display_name(profile_unique_name)

        key = ndb.Key('Profile', profile_unique_name)
        qry = cls.query(ancestor=key)

        profile_inst = qry.get()

        return profile_inst

    @classmethod
    def get_profile_by_application_user_id(cls, application_user_id):
        if application_user_id is not None:
            application_user_id = str(application_user_id)

        if application_user_id is None or re.match(r"^\s*$", application_user_id):
            raise ValueError("Profile.get_profile_by_application_user_id requires an application_user_id")

        application_user_id = application_user_id.strip()
        qry = cls.query(Profile.application_user_id == application_user_id)

        profile_inst = qry.get()

        return profile_inst

    @classmethod
    def add_profile(cls, profile_unique_display_name, application_user_id, bio=None, profile_picture=None):
        if profile_unique_display_name is None or re.match(r"^\s*$", profile_unique_display_name):
            raise ValueError("Profile.add_profile requires a valid profile name.")
        elif not re.search(r"[A-Za-z0-9]", profile_unique_display_name):
            raise ValueError("Profile.add_profile called with an invalid profile_unique_display_name. " +
                             "The profile_unique_display_name must contain a letter and, or a number.")

        profile_unique_name = Profile.get_profile_unique_name_from_profile_display_name(profile_unique_display_name)

        if application_user_id is not None:
            application_user_id = str(application_user_id)
            application_user_id = application_user_id.strip()

        if application_user_id is None or re.match(r"^\s*$", application_user_id):
            raise ValueError("Profile.add_profile requires an application_user_id")
        elif not re.match(r"^[A-Za-z0-9][A-Za-z0-9\-]+[A-Za-z0-9]+$", application_user_id):
            raise ValueError(("Profile.add_profile application_user_id='%s' is not a valid application user ID. " +
                              "The application_user_id should consist of letters, numbers, and dashes, and must " +
                              "begin and end with a letter or a number") % application_user_id)

        profile_obj = Profile.get_profile_by_profile_unique_name(profile_unique_display_name)

        if profile_obj is not None:
            raise UniquenessConstraintViolatedException(("Cannot add the given profile. " +
                                                         "A profile already exists with " +
                                                         "the profile_unique name '%s'.") % profile_unique_name)

        profile_obj = Profile.get_profile_by_application_user_id(application_user_id)

        if profile_obj is not None:
            raise UniquenessConstraintViolatedException(("Cannot add the profile '%s'. The user with ID '%s' already " +
                                                         "has a profile under the name '%s'.") %
                                                        (profile_unique_name, profile_obj.application_user_id,
                                                         profile_obj.profile_unique_name))

        key = ndb.Key('Profile', profile_unique_name)

        profile_obj = Profile(parent=key,
                              profile_unique_display_name=profile_unique_display_name,
                              profile_unique_name=profile_unique_name,
                              application_user_id=application_user_id)

        if bio is not None and not re.match(r"^\s*$", bio):
            bio = bio.strip()
            profile_obj.bio = bio

        if profile_picture is not None:
            profile_obj.profile_picture = profile_picture

        profile_obj.put()

        return profile_obj
