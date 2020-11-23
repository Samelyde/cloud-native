from mongoengine import *

class Photo(Document):
    title = StringField(max_length=120)
    location = StringField(max_length=120)
    author = StringField(max_length=120, required=True)
    comment = StringField(max_length=120)
    tags = ListField(StringField(max_length=30))
    photo = ImageField(required=True)

