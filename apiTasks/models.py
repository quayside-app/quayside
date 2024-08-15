from django.db import models
from apiAccounts.models import Profile
from apiProjects.models import Project, Status


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
