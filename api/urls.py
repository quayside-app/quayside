import importlib
from django.urls import path, include
import apiAccounts


API_VERSION = "v1"
#versionedModule = importlib.import_module(name=f".{API_VERSION}", package="api")


# Remember to add class to views/{version}/__init__.py
urlpatterns = [
    # path(
    #     f"{API_VERSION}/users/",
    #     apiAccounts.ProfilesAPIView.as_view(),
    #     name=f"{API_VERSION}-get-user",
    # ),
    # path(
    #     f"{API_VERSION}/projects/",
    #     versionedModule.projects.ProjectsAPIView.as_view(),
    #     name=f"{API_VERSION}-projects-list",
    # ),
    # path(
    #     f"{API_VERSION}/statuses/",
    #     versionedModule.statuses.StatusesAPIView.as_view(),
    #     name=f"{API_VERSION}-status-list",
    # ),
    # path(
    #     f"{API_VERSION}/tasks/",
    #     versionedModule.tasks.TasksAPIView.as_view(),
    #     name=f"{API_VERSION}-tasks-list",
    # ),
    # path(
    #     f"{API_VERSION}/generatedTasks/",
    #     versionedModule.generatedTasks.GeneratedTasksAPIView.as_view(),
    #     name=f"{API_VERSION}-generated-tasks",
    # ),
    # path(
    #     f"{API_VERSION}/kanban/",
    #     versionedModule.kanban.KanbanAPIView.as_view(),
    #     name=f"{API_VERSION}-kanban-board"
    # ),
    # path(
    #     f"{API_VERSION}/feedback/",
    #     versionedModule.feedback.FeedbackAPIView.as_view(),
    #     name=f"{API_VERSION}-feedback"
    # ),
]

# GET /api/v1/users/:username                   Get information about a user
#           no req
#           res = {email:String, username:String, firstName:String, lastName:String}


# GET /api/v1/projects?uid={}&projectID={}      Get a some form of a list of projects
# GET /api/v1/project/:projectID                Get an individual project
# GET /api/v1/search                            Search for something at some point; do later
# GET /api/v1/project/:projectID/tasks
