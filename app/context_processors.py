import os
import jwt
from rest_framework import status
from dotenv import load_dotenv
from django.http import HttpResponseServerError

from apiAccounts.views import ProfilesAPIView
from app.forms import NewProjectForm


def global_context(request):
    """
    Sets context variables used by EVERY HTML template.
    Currently sets the profileID and api version url.

    @param {HttpRequest} request - The request object.
    @returns {dict} - A dictionary with the API URL and the user ID,
        where the user ID is an empty string if not authenticated.
    """

    # Get profileID from jwt if they are logged in
    load_dotenv()
    secretKey = os.getenv("API_SECRET")
    token = request.COOKIES.get("apiToken")

    profileID = ""
    username = ""
    if token:
        decoded = jwt.decode(token, secretKey, algorithms=["HS256"])
        profileID = decoded.get("profileID")

        data, httpsCode = ProfilesAPIView.getProfiles({"id": profileID}, token)
        if httpsCode != status.HTTP_200_OK:
            print(f"User get failed: {data.get('message')}")
            return HttpResponseServerError(f"An error occurred: {data.get('message')}")
        username = data[0].get("username")

    return {
        "apiUrl": "/api/v1",
        "profileID": profileID,
        "username": username,
        "newProjectForm": NewProjectForm(),
    }
