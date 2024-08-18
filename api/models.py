from django.db import models
from django.conf import settings

from bson.objectid import ObjectId
from datetime import datetime, timezone

from apiAccounts.models import Profile
from apiProjects.models import Project
from apiTasks.models import Task

# TODO: Take out "ID" from all user names
# TODO: Soft delete for user but not in db (tasks, projects) then fix cascades
# TODO: Archive flag




class Feedback(models.Model):
    profileID = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)  # TODO: Null may be better?  # Rename to profile
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    taskID = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    dateCreated = models.DateField(auto_now_add=True)
    mood = models.IntegerField()  # TODO: Change to string??
    explanation = models.TextField()
