import mongoengine as mongo


class User(mongo.Document):
    email = mongo.EmailField(required=True, unique=True)
    username = mongo.StringField(required=True)  #     , unique=True)
    firstName = mongo.StringField()
    lastName = mongo.StringField()
    teamIDs = mongo.ListField(mongo.ObjectIdField())
    apiKey = mongo.StringField()
    meta = {
        "collection": "User",  # Need to specify UPPER Case
        "strict": False,  # If true, throws weird error for __v
    }

    class Meta:
        ordering = ["created"]


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
    contributorIDs = mongo.ListField(mongo.ObjectIdField())
    completionRequirements = mongo.ListField(mongo.StringField())
    qualityAssurance = mongo.ListField(mongo.StringField())
    KPIs = mongo.ListField(mongo.StringField())
    otherProjectDependencies = mongo.ListField(mongo.ObjectIdField())
    informationLinks = mongo.ListField(mongo.StringField())
    completionStatus = mongo.StringField()
    teams = mongo.ListField(mongo.ObjectIdField())
    meta = {
        "collection": "Project",  # Need to specify UPPER Case
        "strict": False,  # If true, throws weird error for __v
    }


class Task(mongo.Document):
    projectID = mongo.ObjectIdField()
    parentTaskID = mongo.ObjectIdField(null=True)  # Allow null values
    name = mongo.StringField()
    objectives = mongo.ListField(mongo.StringField())
    scopesIncluded = mongo.ListField(mongo.StringField())
    scopesExcluded = mongo.ListField(mongo.StringField())
    contributorIDs = mongo.ListField(mongo.ObjectIdField())
    otherProjectDependencies = mongo.ListField(mongo.ObjectIdField())
    otherTaskDependencies = mongo.ListField(mongo.ObjectIdField())
    description = mongo.StringField(null=True)
    startDate = mongo.DateField(null=True)
    endDate = mongo.DateField(null=True)
    kanbanStatus = mongo.StringField(default="Todo")

    meta = {
        "collection": "Task",  # Need to specify UPPER Case
        "strict": False,  # If true, throws weird error for __v
    }
