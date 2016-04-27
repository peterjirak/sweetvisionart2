from google.appengine.ext import ndb
from models.profile import Profile


class Art(ndb.Model):
    application_user_id = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    image = ndb.BlobProperty()
    createDate = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_art(cls, application_user_id=None):
        qry = cls.query().order(-cls.createDate)
        if application_user_id:
            qry = cls.query(Art.application_user_id == application_user_id).order(-cls.createDate)
        art = qry.fetch(20)

        return art

    @classmethod
    def get_art_by_id(cls, id):
        art = cls.get_by_id(id)
        if art:
            return art
