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

class Project(mongo.Document):
    name = mongo.StringField()
    types = mongo.ListField(mongo.StringField())
    objectives = mongo.ListField(mongo.StringField())
    startDate = mongo.DateField()
    endDate = mongo.DateField()
    budget = mongo.StringField()
    assumptions = mongo.ListField(mongo.StringField())
    scopesIncluded = mongo.ListField(mongo.StringField())
    scopesExcluded = mongo.ListField(mongo.StringField())
    risks = mongo.ListField(mongo.StringField())
    userIDs = mongo.ListField(mongo.ObjectIdField())
    projectManagerIDs = mongo.ListField(mongo.ObjectIdField())
    sponsors = mongo.ListField(mongo.StringField())
    contributerIDs = mongo.ListField(mongo.ObjectIdField())
    completionRequirements = mongo.ListField(mongo.StringField())
    qualityAssurance = mongo.ListField(mongo.StringField())
    KPIs = mongo.ListField(mongo.StringField())
    otherProjectDepencies = mongo.ListField(mongo.ObjectIdField())
    informationLinks = mongo.ListField(mongo.StringField())
    completionStatus = mongo.StringField()
    teams = mongo.ListField(mongo.ObjectIdField())
    meta = {
        'collection': 'Project', # Need to specify UPPER Case
        'strict': False  # If true, throws weird error for __v
        } 


