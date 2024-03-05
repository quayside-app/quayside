from django.urls import path
import importlib

API_VERSION = "v1"
views = importlib.import_module(name=f".views.{API_VERSION}", package="api")


# Remember to add class to views/{version}/__init__.py
urlpatterns = [
    path(f"{API_VERSION}/users/",
         views.users.UsersAPIView.as_view(), name=f"{API_VERSION}-get-user"),

#     path(f"{API_VERSION}/users/create/",
#          views.createUser.CreateUserAPIView.as_view(), name=f"{API_VERSION}-create-user"),

    path(f"{API_VERSION}/projects/",
         views.projects.ProjectsAPIView.as_view(), name=f"{API_VERSION}-projects-list"),
     
    path(f"{API_VERSION}/project/<str:id>/",
         views.project.ProjectAPIView.as_view(), name=f"{API_VERSION}-project-details"),
    path(f"{API_VERSION}/tasks/",
         views.tasks.TasksAPIView.as_view(), name=f"{API_VERSION}-tasks-list")
]

# GET /api/v1/users/:username                   Get information about a user
#           no req
#           res = {email:String, username:String, firstName:String, lastName:String}


# GET /api/v1/projects?uid={}&projectID={}      Get a some form of a list of projects
# GET /api/v1/project/:projectID                Get an individual project
# GET /api/v1/search                            Search for something at some point; do later
# GET /api/v1/project/:projectID/tasks

