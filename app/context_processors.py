import os
import jwt
from rest_framework import status
from dotenv import load_dotenv
from django.http import HttpResponseServerError

from api.views.v1.users import UsersAPIView
from app.forms import NewProjectForm



def global_context(request):
    """
    Sets context variables used by EVERY HTML template.
    Currently sets the userID and api version url.

    @param {HttpRequest} request - The request object.
    @returns {dict} - A dictionary with the API URL and the user ID,
        where the user ID is an empty string if not authenticated.
    """


    # Get userID from jwt if they are logged in
    load_dotenv()
    secretKey = os.getenv("API_SECRET")
    token = request.COOKIES.get("apiToken")

    userID = ""
    username = ""
    if token:
        decoded = jwt.decode(token, secretKey, algorithms=["HS256"])
        userID = decoded.get("userID")

        data, httpsCode = UsersAPIView.getUsers({"id": userID}, token)
        if httpsCode != status.HTTP_200_OK:
            print(f"User update failed: {data.get('message')}")
            return HttpResponseServerError(f"An error occurred: {data.get('message')}")
        username = data[0].get("username")


    return {
        "apiUrl": "/api/v1",
        "userID": userID,
        "username": username,
        "newProjectForm": NewProjectForm(),
    }
