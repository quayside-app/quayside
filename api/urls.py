from django.urls import path
import importlib

API_VERSION = "v1"
views = importlib.import_module(name=f".views.{API_VERSION}", package="api")


urlpatterns = [
    path(f"{API_VERSION}/users/<str:username>/",
         views.users.UserDetailAPIView.as_view(), name="v1-user-detail"),
    path(f"{API_VERSION}/projects/",
         views.projects.ProjectsAPIView.as_view(), name="v1-projects"),
]

# GET /api/v1/users/:username                   Get information about a user
#           no req
#           res = {email:String, username:String, firstName:String, lastName:String}


# GET /api/v1/projects?uid={}&projectID={}      Get a some form of a list of projects
# GET /api/v1/project/:projectID                Get an individual project
# GET /api/v1/search                            Search for something at some point; do later
# GET /api/v1/project/:projectID/tasks
