
from api.views.v1.tasks import TasksAPIView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import NewProjectForm, TaskForm
from api.views.v1.generatedTasks import GeneratedTasksAPIView
from api.views.v1.projects import ProjectsAPIView

from api.views.v1.users import UsersAPIView
from oauthlib.oauth2 import WebApplicationClient as WAC
import requests

import os
from django.views.generic.base import TemplateView

from api.decorators import apiKeyRequired
from app.context_processors import global_context

from api.utils import decryptApiKey, createEncodedApiKey, encryptApiKey



def userLogin(request):
    """
    Renders the login model for the user.

    @param {HttpRequest} request - The request object.
    @returns {HttpResponse} - An HttpResponse object that renders the login.html template.
    """
    return render(request, 'login.html')



@apiKeyRequired
def projectGraphView(request, projectID):
    """
    Renders the graph view for a specific project. This view requires an API key in the cookies.


    @param {HttpRequest} request - The request object.
    @param {str} projectID - The ID for the project whose graph is to be rendered.
    @returns {HttpResponse} - An HttpResponse object that renders the 
        graph.html template with the project ID context.
    """
    return render(request, "graph.html", {"projectID": projectID})

@apiKeyRequired
def taskView(request, projectID, taskID):
    """
    Renders the view for a specific task within a project as a form. 
    If the request method is GET or any other method, a form populated with the task's existing 
    data is provided for editing or a blank form for creation.
    If the request method is POST and the form is valid, the task is updated with the provided data. 
    This view requires an API key in the cookies.

    @param {HttpRequest} request - The request object, which can be GET or POST.
    @param {str} projectID - The ID for the project to which the task belongs.
    @param {str} taskID - The ID for the task to be viewed or edited.
    
    @returns {HttpResponse} - An HttpResponse object that renders the taskModal.html 
        template with the project ID, task ID, and task form context.
    """
    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            newData = form.cleaned_data
            newData["id"] = taskID
            data, code = TasksAPIView.updateTask(newData)

    # If a GET (or any other method) we"ll create a blank form
    else:
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
    return render(request, "taskModal.html", {"projectID": projectID, "taskID": taskID, "form": form})

@apiKeyRequired
def createProjectView(request):
    """
    Renders the view for creating a new project. 
    If the method is POST, it processes the submitted form data to create a new project. 
    If the method is GET or any other, it presents a blank form for creating a project. 
    This view requires an API key in the cookies.

    @param {HttpRequest} request - The request object, which determines the behavior (GET or POST) of the view.
    @returns {HttpResponse} - An HttpResponse object that either renders the newProjectModal.html template with the form or redirects to the project's graph view upon successful creation.

    """

    # Gets userID from global context
    context = global_context(request)
    userId = context.get('userID')

    # If this is a POST request, process the form data
    if request.method == "POST":
        form = NewProjectForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            name = form.cleaned_data["description"]

            projectData, _ = ProjectsAPIView.createProjects({"name": name, "userIDs": [userId]}) 
            projectID = projectData.get("id")
            GeneratedTasksAPIView.generateTasks(
                {"projectID": projectID, "name": name})

            # Redirect to project
            return HttpResponseRedirect(f"/project/{projectID}/graph")

    # If a GET (or any other method), create a blank form
    else:
        form = NewProjectForm()

    return render(request, "newProjectModal.html", {"form": form})


def requestAuth(request):
    """
    Initiates an OAuth authentication request (Github, etc).

    @param {HttpRequest} request - The request object.
    @returns {HttpResponseRedirect} - A redirect response that navigates the user to OAuth 
        authorization page.
    """
    clientID = os.getenv("GITHUB_CLIENT_ID")
    client = WAC(clientID)
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
        """
        Handles the callback after GitHub authentication, creates the user in the db if they
        don't exist, and retrieves the user's info and API key (generating it if it doesn't exist).
        It then saves the API key to the user's cookies so it can be sent to the API routes in
        future requests.

        @param request: The HTTP request object containing the callback data from GitHub.
        @returns: The rendered index.html page with the API token set in the cookies.
        """
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

        oathUserInfo = response.json()
        # For Github, if user has no visible email, make second request for email
        if not oathUserInfo.get('email'):
            response = requests.get(
                os.getenv('GITHUB_API_URL_email'), headers=header)
            oathUserInfo['email'] = response.json()[0]['email']

        
        userInfo = UsersAPIView.getUser(
            {'email': oathUserInfo.get('email')})[0].get("user")

        # Create a user in our db if none exists
        if not userInfo:
            names = oathUserInfo.get('name').split()
            userInfo, _ = UsersAPIView.createUser({'email': oathUserInfo['email'],
                                                'username': oathUserInfo.get('login'),
                                                'firstName': names[0],
                                                'lastName': names[-1],
                                                })
        response = redirect('/')  # Redirect instead of rendering (to make it update)


        apiToken = userInfo.get("apiKey") # Get API key 
        
        if apiToken:
            apiToken = decryptApiKey(apiToken)
        # Create an api key if it doesn't exist in the db yet
        else:
            # Create/encrypt API key
            apiToken = createEncodedApiKey(userInfo["id"])
            encryptedApiKey = encryptApiKey(apiToken)

            # Save api Key to DB
            userInfo, _ = UsersAPIView.updateUser({'id': userInfo["id"],
                                                'apiKey': encryptedApiKey,
                                                })

        # Save api key to cookies
        # Setting httponly is safer and doesn't let the key be accessed by js (to prevent xxs).
        # Instead the browser will always pass the cookie to the server.
        response.set_cookie('apiToken', apiToken, httponly=True)

        return response

