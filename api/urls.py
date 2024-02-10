from django.urls import path
import importlib

VERSION = "v1"
#views_module = importlib.import_module(f"views.{VERSION}", package="quayside-api")
from .views.v1 import users



urlpatterns = [
    path(f"{VERSION}/users/<str:username>/", users.UserDetailAPIView.as_view(), name="v1-user-detail"),
]

# GET /api/v1/users/:username                   Get information about a user
#           no req
#           res = {email:String, username:String, firstName:String, lastName:String}



# GET /api/v1/projects?uid={}&projectID={}      Get a some form of a list of projects
# GET /api/v1/project/:projectID                Get an individual project
# GET /api/v1/search                            Search for something at some point; do later
# GET /api/v1/project/:projectID/tasks