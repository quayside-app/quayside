from django.db import models
from apiAccounts.models import Profile

class Project(models.Model):
    name = models.CharField(max_length=255)  # TODO LIMIT ON FRONT END
    description = models.TextField(null=True, blank=True)
    startDate = models.DateField(null=True)  
    endDate = models.DateField(null=True) 
    profileIDs = models.ManyToManyField(Profile, related_name='project') # Django handles as intermediary join table # TODO: split into owner, editor, and viewer 

class Status(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name =  models.CharField(max_length=255)  # TODO LIMIT ON FRONT END
    color = models.CharField(max_length=16)  # Hex color code
    order = models.IntegerField()  # Task order on kanban