import mongoengine as mongo
from datetime import datetime


class User(mongo.Document):
    email = mongo.EmailField(required=True, unique=True)
    username = (
        mongo.StringField()
    )  # Can not be required or messes up updates#required=True)  #     , unique=True)
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
    description = mongo.StringField(null=True)
    types = mongo.ListField(mongo.StringField())
    objectives = mongo.ListField(mongo.StringField())
    startDate = mongo.DateField(null=True)  # Allow null values
    endDate = mongo.DateField(null=True)  # Allow null values
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
    status = mongo.StringField(default='Todo', choices=('In-Progress', 'Todo', 'Done'))
    priority = mongo.IntField(null=True)
    durationMinutes = mongo.IntField(null=False)

    meta = {
        "collection": "Task",  # Need to specify UPPER Case
        "strict": False,  # If true, throws weird error for __v
    }

class TermsAndConditions(mongo.Document):
    version = mongo.StringField(required=True, unique=True)
    content = mongo.StringField(required=True)
    created_at = mongo.DateTimeField(default=datetime.now)

    meta = {
        "collection": "TermsAndConditions",
        "ordering": ["-created_at"],
        "strict": False
    }

    def __str__(self):
        return f"Terms {self.version}"

class UserTermsAcceptance(mongo.Document):
    user = mongo.ReferenceField("User", required=True, unique=True)
    accepted_version = mongo.StringField(required=True)
    accepted_at = mongo.DateTimeField(default=datetime.now)

    meta = {
        "collection": "UserTermsAcceptance",
        "strict": False
    }

    def __str__(self):
        return f"{self.user.email} accepted {self.accepted_version}"
