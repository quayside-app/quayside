
from api.views.v1.tasks import TasksAPIView
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import NewProjectForm, TaskForm
from api.views.v1.generatedTasks import GeneratedTasks
from api.views.v1.projects import ProjectsAPIView

from api.views.v1.users import UsersAPIView
from oauthlib.oauth2 import WebApplicationClient as WAC
import requests

import os
from django.views.generic.base import TemplateView
from django.contrib.auth import login
import jwt
from dotenv import load_dotenv

from cryptography.fernet import Fernet
from api.decorators import api_key_required


def user_login(request):
    return render(request, 'login.html')


def user(request):
    print(request)
    return render(request, 'index.html')

@api_key_required
def projectGraphView(request, projectID):
    return render(request, "graph.html", {"project_ID": projectID})

@api_key_required
def taskView(request, projectID, taskID):
    print("IN CREATE TASK VEW")
    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            newData = form.cleaned_data
            newData["id"] = taskID
            print(newData)

            data, code = TasksAPIView.updateTask(newData)

            print("UPDATED TASKS...")

            print(data)
            print(code)

    # if a GET (or any other method) we"ll create a blank form
    else:
        print("HEREEEE")
        taskData = TasksAPIView.getTasks({"id": taskID})[0][0]
        # Populate initial form data
        if taskData is not None:
            initialData = {
                "name": taskData.get("name", ""),
                "description": taskData.get("description", ""),
            }
            form = TaskForm(initial=initialData)
        else:
            form = TaskForm()
    return render(request, "taskModal.html", {"project_ID": projectID, "taskID": taskID, "form": form})

@api_key_required
def createProjectView(request):

    # If this is a POST request, process the form data
    if request.method == "POST":
        form = NewProjectForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            name = form.cleaned_data["description"]

            projectData, _ = ProjectsAPIView.createProjects({"name": name, "userIDs": [
                                                            "6521d8581bcf69b7d260608b"]})  # ! TODO change to not-hardcoded
            projectID = projectData["id"]
            GeneratedTasks.generateTasks(
                {"projectID": projectID, "name": name})

            # Redirect to project
            return HttpResponseRedirect(f"/project/{projectID}/graph")

    # If a GET (or any other method), create a blank form
    else:
        form = NewProjectForm()

    return render(request, "newProjectModal.html", {"form": form})


def RequestAuth(request):
    clientID = os.getenv("GITHUB_CLIENT_ID")
    client = WAC(clientID)
    print(request)
    authorization_url = 'https://github.com/login/oauth/authorize'

    url = client.prepare_request_uri(
        authorization_url,
        redirectURL='http://127.0.0.1:8000/callback',
        scope=['user'],
        state='/'
    )
    return HttpResponseRedirect(url)


class Callback(TemplateView):
    def get(self, request):
        data = self.request.GET
        authcode = data['code']
        state = data['state']

        # Get API token

        token_url = 'https://github.com/login/oauth/access_token'
        clientID = os.getenv("GITHUB_CLIENT_ID")
        clientSecret = os.getenv("GITHUB_CLIENT_SECRET")

        client = WAC(clientID)

        data = client.prepare_request_body(
            code=authcode,
            redirect_uri='http://127.0.0.1:8000/callback',
            client_id=clientID,
            client_secret=clientSecret
        )

        response = requests.post(token_url, data=data)

        client.parse_request_body_response(response.text)

        header = {'Authorization': 'token {}'.format(
            client.token['access_token'])}

        response = requests.get(
            os.getenv('GITHUB_API_URL_user'), headers=header)

        json_dict = response.json()
        # For Github, if user has no visible email, make second request for email
        if json_dict['email'] is None:
            response = requests.get(
                os.getenv('GITHUB_API_URL_email'), headers=header)
            json_dict['email'] = response.json()[0]['email']

        
        userInfo = UsersAPIView.getUser(
            {'email': json_dict.get('email')})[0].get("user")

        # Create a user in our db if none exists
        if not userInfo:
            names = json_dict.get('name').split()
            userInfo, _ = UsersAPIView.createUser({'email': json_dict['email'],
                                                'username': json_dict.get('login'),
                                                'firstName': names[0],
                                                'lastName': names[-1],
                                                })
        response = render(request, 'index.html')

        key = os.getenv('API_SECRET') + "=" # .Env does NOT read "=" properly but fernet requires it
        fernet = Fernet(key.encode())
        apiToken = fernet.decrypt(userInfo.get("apiKey")).decode() # Get API key and decrypt/decode
        # Create an api key if it doesn't exist in the db yet
        if not apiToken:
            # Create api jwt key and save as a cookie
            apiToken = create_api_key(userInfo["id"])

            # Encrypt key to store in db
            encryptedApiKey = fernet.encrypt(apiToken.encode()).decode() # Encode and turn back into a string

            # Save api Key to DB
            userInfo, _ = UsersAPIView.updateUser({'id': userInfo["id"],
                                                'apiKey': encryptedApiKey,
                                                })
            
        # Save api key to cookies
        # Setting httponly is safer and doesn't let the key be accessed by js (to prevent xxs).
        # Instead the browser will always pass the cookie to the server.
        response.set_cookie('apiToken', apiToken, httponly=True)

        return response


def create_api_key(userID: str) -> str:
    load_dotenv()
    secretKey = os.getenv('API_SECRET')
    payload = {
        "userID": userID,
        # "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)  # TODO expiration time
    }

    apiKey = jwt.encode(payload, secretKey, algorithm="HS256")
    return apiKey
