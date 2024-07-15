import importlib
from django.urls import path, include
from oauth2_provider import urls as oauth2_urls



API_VERSION = "v1"
views = importlib.import_module(name=f".views.{API_VERSION}", package="api")


# Remember to add class to views/{version}/__init__.py
urlpatterns = [
    path(
        f"{API_VERSION}/users/",
        views.users.UsersAPIView.as_view(),
        name=f"{API_VERSION}-get-user",
    ),
    path(
        f"{API_VERSION}/projects/",
        views.projects.ProjectsAPIView.as_view(),
        name=f"{API_VERSION}-projects-list",
    ),
    path(
        f"{API_VERSION}/statuses/",
        views.statuses.StatusesAPIView.as_view(),
        name=f"{API_VERSION}-status-list",
    ),
    path(
        f"{API_VERSION}/tasks/",
        views.tasks.TasksAPIView.as_view(),
        name=f"{API_VERSION}-tasks-list",
    ),
    path(
        f"{API_VERSION}/generatedTasks/",
        views.generatedTasks.GeneratedTasksAPIView.as_view(),
        name=f"{API_VERSION}-generated-tasks",
    ),
    path(
        f"{API_VERSION}/kanban/",
        views.kanban.KanbanAPIView.as_view(),
        name=f"{API_VERSION}-kanban-board"
    ),
    path(
        f"{API_VERSION}/feedback/",
        views.feedback.FeedbackAPIView.as_view(),
        name=f"{API_VERSION}-feedback"
    ),
    # path('o/', include(oauth2_urls)),
    path(
        f"{API_VERSION}/users/",
        views.users.UserList.as_view(),
        name=f"{API_VERSION}-get-user",
    ),
]

# GET /api/v1/users/:username                   Get information about a user
#           no req
#           res = {email:String, username:String, firstName:String, lastName:String}


# GET /api/v1/projects?uid={}&projectID={}      Get a some form of a list of projects
# GET /api/v1/project/:projectID                Get an individual project
# GET /api/v1/search                            Search for something at some point; do later
# GET /api/v1/project/:projectID/tasks
