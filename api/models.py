import mongoengine as mongo
from bson.objectid import ObjectId
from datetime import datetime, timezone


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

    def create_default_task_statuses():
            return [
                {
                    "name": "Todo",
                    "color": "323232", # html color code
                    "order": 1 # task order on kanban
                },
                {
                    "name": "In-Progress",
                    "color": "EFA610",
                    "order": 2 # task order on kanban
                },
                {
                    "name": "Done",
                    "color": "01796E", # html color code
                    "order": 3 # task order on kanban
                }
            ]
    
    class Status(mongo.EmbeddedDocument):
        id = mongo.ObjectIdField(default=ObjectId)
        name =  mongo.StringField(null=False, required=True)
        color = mongo.StringField(null=False, required=True) # html color code
        order = mongo.IntField(null=False, required=True) # task order on kanban
        
    taskStatuses = mongo.EmbeddedDocumentListField(Status, default=create_default_task_statuses(), blank=True)

    def clean(self):
        # Ensures all status within a project have unique ids
        ids = [status.id for status in self.taskStatuses]
        if len(ids) != len(set(ids)):
            raise mongo.ValidationError("Duplicate taskStatus IDs found in project.")


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
    # status = mongo.StringField(default='Todo', choices=('In-Progress', 'Todo', 'Done'))
    statusId = mongo.ObjectIdField(null=True, default=None)
    priority = mongo.IntField(null=True)
    durationMinutes = mongo.IntField(null=False)

    meta = {
        "collection": "Task",  # Need to specify UPPER Case
        "strict": False,  # If true, throws weird error for __v
    }

class Feedback(mongo.Document):
    userID = mongo.ObjectIdField(required=True)
    projectID = mongo.ObjectIdField(required=True)
    taskID = mongo.ObjectIdField(null=True)  # for now
    dateCreated = mongo.DateTimeField(default=datetime.now(timezone.utc))
    mood = mongo.IntField(null=0)
    explanation = mongo.StringField(null=True)
    meta = {
        "collection": "Feedback",  # Need to specify for it to be UPPER Case
    }