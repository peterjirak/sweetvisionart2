from google.appengine.ext import ndb

class Profile(ndb.Model):
  user_id = ndb.StringProperty(required=True)
  profile_unique_name = ndb.StringProperty(required=True)
  first_name = ndb.StringProperty(required=True)
  last_name = ndb.StringProperty(required=True)
  middle_name = ndb.StringProperty(required=False)
  bio = ndb.TextProperty(required=False)
  image = ndb.BlobProperty()
  createDate = ndb.DateTimeProperty(auto_now_add=True)