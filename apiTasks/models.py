from django.db import models
from apiAccounts.models import Profile
from apiProjects.models import Project, Status


class Task(models.Model):
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    parentTaskID = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='childTasks')  # TODO: Check this when have more braincells
    name = models.CharField(max_length=255)  # TODO LIMIT ON FRONT END
    description = models.TextField(null=True, blank=True)
    contributorIDs = models.ManyToManyField(Profile, related_name='tasks', blank=True)  # TODO: Change to assigneeIDs  # Django handles as intermediary join table
    startDate = models.DateField(null=True, blank=True)
    endDate = models.DateField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)  # TODO: Change to kanbanOrder and add graphOrder
    durationMinutes = models.IntegerField(null=True, blank=True)
    dateCreated = models.DateField(auto_now_add=True)
    dateLastEdit = models.DateField(null=True, blank=True) # TODO ADD LOGIC FOR THIS
    lastEditor = models.ForeignKey(Profile, on_delete=models.SET("DELETED_PROFILE"), null=True, blank=True)  # TODO: Null on_delete may be better? # TODO: ADD LOGIC IN VIEWS FOR THIS

    # TODO automagically set date when updated
