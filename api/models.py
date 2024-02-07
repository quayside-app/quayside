import mongoengine as mongo


class User(mongo.Document):
    email = mongo.EmailField(required=True)
    username = mongo.StringField(required=True)
    firstName = mongo.StringField()
    lastName = mongo.StringField()
    teamIDs = mongo.ListField(mongo.ObjectIdField())
    meta = {
        'collection': 'User', # Need to specify UPPER Case
        'strict': False  # If true, throws weird error for __v
        }  

