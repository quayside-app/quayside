from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from bson.objectid import ObjectId
from datetime import datetime, timezone

from api.v1.accounts.models import Profile

# TODO: Take out "ID" from all user names
# TODO: Soft delete for user but not in db (tasks, projects) then fix cascades
# TODO: Archive flag





class Project(models.Model):
    name = models.CharField(max_length=255)  # TODO LIMIT ON FRONT END
    description = models.TextField()
    startDate = models.DateField(null=True)  
    endDate = models.DateField(null=True) 
    userIDs = models.ManyToManyField(User, related_name='projects')  # TODO: split into owner, editor, and viewer # Django handles as intermediary join table

class Status(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name =  models.CharField(max_length=255)  # TODO LIMIT ON FRONT END
    color = models.CharField(max_length=16)  # Hex color code
    order = models.IntegerField()  # Task order on kanban
    

class Task(models.Model):
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    parentTaskID = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # TODO: Check this when have more braincells
    name = models.CharField(max_length=255)  # TODO LIMIT ON FRONT END
    description = models.TextField()
    contributorIDs = models.ManyToManyField(Profile, related_name='tasks')  # TODO: Change to assigneeIDs  # Django handles as intermediary join table
    startDate = models.DateField()
    endDate = models.DateField()
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    priority = models.IntegerField()  # TODO: Change to kanbanOrder and add graphOrder
    durationMinutes = models.IntegerField()
    dateCreated = models.DateField(auto_now_add=True)
    dateLastEdit = models.DateField()
    lastEditor = models.ForeignKey(Profile, on_delete=models.SET("DELETED_PROFILE"))  # TODO: Null may be better?

    # TODO automagically set date when updated

class Feedback(models.Model):
    userID = models.ForeignKey(Profile, on_delete=models.SET("DELETED_PROFILE"))  # TODO: Null may be better?  # Rename to profile
    projectID = models.ForeignKey(Project, on_delete=models.SET("DELETED_PROFILE"))
    taskID = models.ForeignKey(Task, on_delete=models.SET("DELETED_PROFILE"))
    dateCreated = models.DateField(auto_now_add=True)
    mood = models.IntegerField()  # TODO: Change to string??
    explanation = models.TextField()
