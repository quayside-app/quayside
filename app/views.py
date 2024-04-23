import os
import re
import urllib.parse
import requests
from oauthlib.oauth2 import WebApplicationClient as WAC
from rest_framework import status


from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.base import TemplateView

from api.decorators import apiKeyRequired
from api.utils import (
    decryptApiKey,
    createEncodedApiKey,
    encryptApiKey,
    getAuthorizationToken,
    decodeApiKey,
)
from api.views.v1.tasks import TasksAPIView
from api.views.v1.generatedTasks import GeneratedTasksAPIView
from api.views.v1.projects import ProjectsAPIView
from api.views.v1.users import UsersAPIView

from app.context_processors import global_context
from app.forms import NewProjectForm, TaskForm, ProjectForm


def redirectOffSite(_request):
    return redirect("https://github.com/quayside-app/quayside")


def logout(_request):
    response = redirect("/")
    response.delete_cookie("apiToken")
    response.delete_cookie("csrftoken")
    response.delete_cookie("sessionid")
    return response


@apiKeyRequired
def projectGraphView(request, projectID):
    """
    Renders the graph view for a specific project. This view requires an API key in the cookies.


    @param {HttpRequest} request - The request object.
    @param {str} projectID - The ID for the project whose graph is to be rendered.
    @returns {HttpResponse} - An HttpResponse object that renders the
        graph.html template with the project ID context.
    """
    # Check if project exists
    data, httpsCode = ProjectsAPIView.getProjects(
        {"id": projectID}, getAuthorizationToken(request)
    )

    if httpsCode != status.HTTP_200_OK:
        print(f"Project GET failed: {data.get('message')}")
        return HttpResponseServerError(
            f"Could not query project: {data.get('message')}"
        )

    return render(
        request, "graph.html", {"projectID": projectID, "projectData": data[0]}
    )


@apiKeyRequired
def projectKanbanView(request, projectID):
    """
    Renders the graph view for a specific project. This view requires an API key in the cookies.


    @param {HttpRequest} request - The request object.
    @param {str} projectID - The ID for the project whose graph is to be rendered.
    @returns {HttpResponse} - An HttpResponse object that renders the
        graph.html template with the project ID context.
    """
    return render(request, "kanban.html", {"projectID": projectID})

@apiKeyRequired
def projectKanbanView(request, projectID):
    """
    Renders the graph view for a specific project. This view requires an API key in the cookies.


    @param {HttpRequest} request - The request object.
    @param {str} projectID - The ID for the project whose graph is to be rendered.
    @returns {HttpResponse} - An HttpResponse object that renders the
        graph.html template with the project ID context.
    """
    return render(request, "kanban.html", {"projectID": projectID})


@apiKeyRequired
def editProjectView(request, projectID):
    """
    Renders the view for a specific project.
    If the request method is GET or any other method, a form populated with the projects's existing
    data is provided for editing or a blank form for creation.
    If the request method is POST and the form is valid, the project is updated with the provided data.
    This view requires an API key in the cookies.

    @param {HttpRequest} request - The request object, which can be GET or POST.
    @param {str} projectID - The ID for the project.

    @returns {HttpResponse} - An HttpResponse object that renders the taskModal.html
        template with the project ID, task ID, and task form context.
    """
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            newData = form.cleaned_data
            newData["id"] = projectID

            # Replace user emails with userIDs to save

            # Splits on comma, space, or newline. Makes sure only unique emails
            emails = set(re.split(r"\s*[, \n]+\s*", newData["contributors"].strip()))
            # Filter out empty strings
            emails = {email for email in emails if email}

            userIDs = []
            if emails:
                del newData["contributors"]
                emails = [{"email": email} for email in emails if email]

                contributorData, httpsCode = UsersAPIView.getUsers(emails)
                if httpsCode != status.HTTP_200_OK:
                    print(
                        f"Could not query contributor ids for project: {contributorData.get('message')}"
                    )
                    return HttpResponseServerError(
                        f"Could not query contributor ids for project: {contributorData.get('message')}"
                    )

                userIDs = [user["id"] for user in contributorData]

            currentUserID = decodeApiKey(getAuthorizationToken(request)).get("userID")
            if currentUserID not in userIDs:
                userIDs.append(currentUserID)

            newData["userIDs"] = userIDs
            message, httpsCode = ProjectsAPIView.updateProject(
                newData, getAuthorizationToken(request)
            )
            if httpsCode != status.HTTP_200_OK:
                print(f"Task update failed: {message}")
                return HttpResponseServerError(f"An error occurred: {message}")

            return redirect(f"/project/{projectID}/graph")

    # If a GET (or any other method) we"ll create a blank form
    else:
        projectData, httpsCode = ProjectsAPIView.getProjects(
            {"id": projectID}, getAuthorizationToken(request)
        )
        if httpsCode != status.HTTP_200_OK:
            print(f"Project GET failed: {projectData.get('message')}")
            return HttpResponseServerError(
                f"Could not query project: {projectData.get('message')}"
            )

        projectData = projectData[0]

        # Get contributor emails
        contributorString = ""
        currentUserID = decodeApiKey(getAuthorizationToken(request)).get("userID")
        userIDs = projectData.get("userIDs")

        contributorIDs = [{"id": ID} for ID in userIDs if ID != currentUserID]
        if contributorIDs:
            contributorData, httpsCode = UsersAPIView.getUsers(contributorIDs)
            if httpsCode != status.HTTP_200_OK:
                print(
                    f"Could not query contributor emails for project: {contributorData.get('message')}"
                )
                return HttpResponseServerError(
                    f"Could not query contributor emails for project: {contributorData.get('message')}"
                )

            contributorString = ", ".join(
                [contributor["email"] for contributor in contributorData]
            )

        if projectData is not None:
            initialData = {
                "name": projectData.get("name", ""),
                "startDate": projectData.get("startDate", ""),
                "endDate": projectData.get("endDate", ""),
                "contributors": contributorString,
            }
            form = ProjectForm(initial=initialData)
        else:
            form = ProjectForm()
    return render(
        request,
        "projectModel.html",
        {
            "form": form,
            "projectID": projectID,
            "submitLink": f"/project/{projectID}/",
            "exitLink": f"/project/{projectID}/graph",
        },
    )


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

    if "kanban" in request.path:
        baseTemplate = "kanban.html"
        submitLink = f"/project/{projectID}/kanban/task/{taskID}"
        exitLink = f"/project/{projectID}/kanban"
        deleteLink = f"/project/{projectID}/kanban"
    else:
        baseTemplate = "graph.html"
        submitLink = f"/project/{projectID}/graph/task/{taskID}/"
        exitLink = f"/project/{projectID}/graph"
        deleteLink = f"/project/{projectID}/graph"
    if request.method == "POST":

        form = TaskForm(request.POST)

        if form.is_valid():
            newData = form.cleaned_data
            newData["id"] = taskID
            message, status_code = TasksAPIView.updateTask(
                newData, getAuthorizationToken(request)
            )
            if status_code != status.HTTP_200_OK:
                print(f"Task update failed: {message.get('message')}")
                return HttpResponseServerError(
                    f"An error occurred: {message.get('message')}"
                )
            return redirect(f"/project/{projectID}/graph")

    # If a GET (or any other method) we"ll create a blank form
    else:
        data, status_code = TasksAPIView.getTasks(
            {"id": taskID}, getAuthorizationToken(request)
        )
        if status_code != status.HTTP_200_OK:
            print(f"Task fetch failed: {data.get('message')}")
            return HttpResponseServerError(f"An error occurred: {data.get('message')}")

        taskData = data[0]
        # Populate initial form data
        if taskData is not None:
            initialData = {
                "name": taskData.get("name", ""),
                "description": taskData.get("description", ""),
                "status": taskData.get("status", ""),
                "startDate": taskData.get("startDate", ""),
                "endDate": taskData.get("endDate", ""),
            }
            form = TaskForm(initial=initialData)
        else:
            form = TaskForm()
    return render(
        request,
        "taskModal.html",
        {
            "form": form,
            "projectID": projectID,
            "taskID": taskID,
            "baseTemplate": baseTemplate,
            "submitLink": submitLink,
            "exitLink": exitLink,
            "deleteLink": deleteLink,
        },
    )


@apiKeyRequired
def createTaskView(request, projectID, parentTaskID=""):
    """
    Renders the view for creating a task within a project as a form.
    If the request method is GET or any other method, a blank form is provied.
    If the request method is POST and the form is valid, the task is created with the provided data.
    This view requires an API key in the cookies.

    @param {HttpRequest} request - The request object, which can be GET or POST.
    @param {str} projectID - The project ID of the task to create.
    @param {str} parentTaskID [optional] - The parent ID of the task to create.

    @returns {HttpResponse} - An HttpResponse object that renders the taskModal.html
        template with the project ID, task ID, and task form context.
    """
    if "kanban" in request.path:
        baseTemplate = "kanban.html"
        if parentTaskID:
            submitLink = f"/project/{projectID}/kanban/create-task/{parentTaskID}/"
        else:
            submitLink = f"/project/{projectID}/kanban/create-task/"
        exitLink = f"/project/{projectID}/kanban"
    else:
        baseTemplate = "graph.html"
        if parentTaskID:
            submitLink = f"/project/{projectID}/graph/create-task/{parentTaskID}/"
        else: 
            submitLink = f"/project/{projectID}/graph/create-task/"
        exitLink = f"/project/{projectID}/graph"

    # Create new task on post
    if request.method == "POST":

        form = TaskForm(request.POST)

        if form.is_valid():
            newData = form.cleaned_data
            newData["projectID"] = projectID
            if parentTaskID and parentTaskID != "":
                newData["parentTaskID"] = parentTaskID
            message, httpsCode = TasksAPIView.createTasks(
                newData, getAuthorizationToken(request)
            )

            if httpsCode != status.HTTP_201_CREATED:
                print(f"Task creation failed: {message}")
                return HttpResponseServerError(
                    f"An error occurred: {message.get('message')}"
                )
        if "kanban" in request.path:
            return redirect(f"/project/{projectID}/kanban")

        return redirect(f"/project/{projectID}/graph")

    # If a GET (or any other method) we"ll create a blank form for them to render
    else:
        # Check if user has access to project
        projectData, httpsCode = ProjectsAPIView.getProjects(
            {"id": projectID}, getAuthorizationToken(request)
        )
        if httpsCode != status.HTTP_200_OK:
            print(
                f"For creating tasks, project GET failed: {projectData.get('message')}"
            )
            return HttpResponseServerError(
                f"Could not access project to create task(s): {projectData.get('message')}"
            )
        form = TaskForm()
    return render(
        request,
        "taskModal.html",
        {
            "form": form,
            "projectID": projectID,
            "baseTemplate": baseTemplate,
            "submitLink": submitLink,
            "exitLink": exitLink,
        },
    )


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
    userId = context.get("userID")

    # If this is a POST request, process the form data
    if request.method == "POST":
        form = NewProjectForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]

            projectData, httpsCode = ProjectsAPIView.createProjects(
                {
                    "name": name,
                    "description": description, 
                    "userIDs": [userId]
                }, getAuthorizationToken(request)
            )
            if httpsCode != status.HTTP_201_CREATED:
                print(f"Project Creation failed: {projectData.get('message')}")
                return HttpResponseServerError(
                    f"Could not create project: {projectData.get('message')}"
                )

            projectID = projectData.get("id")

            message, httpsCode = GeneratedTasksAPIView.generateTasks(
                {
                    "projectID": projectID, 
                    "name": name,
                    "description": description,
                }
            , getAuthorizationToken(request)
            )
            if httpsCode != status.HTTP_201_CREATED:
                print(f"Task generation failed: {projectData.get('message')}")
                return HttpResponseServerError(
                    f"Could not generate tasks: {message.get('message')}"
                )

            # Redirect to project
            return HttpResponseRedirect(f"/project/{projectID}/graph")

    # If a GET (or any other method), create a blank form
    # else:
    # form = NewProjectForm()
    # If anything else throw error
    # return render(request, "newProjectModal.html", {"form": form})
    return HttpResponseServerError("Only POSTs are allowed for createProjectView")
    # return redirect(request.META.get('HTTP_REFERER', '/'))



@apiKeyRequired
def settingsView(request):
    return render(request, "settings.html", {})


@apiKeyRequired
def inviteView(request):
    return render(request, "invite.html", {})


@apiKeyRequired
def tutorialView(request):
    return render(request, "tutorial.html", {})


@apiKeyRequired
def marketplaceView(request):
    return render(request, "marketplace.html", {})


@apiKeyRequired
def feedbackView(request):
    return render(request, "feedback.html", {})


@apiKeyRequired
def settingsView(request):
    return render(request, "settings.html", {})


@apiKeyRequired
def inviteView(request):
    return render(request, "invite.html", {})


@apiKeyRequired
def tutorialView(request):
    return render(request, "tutorial.html", {})


@apiKeyRequired
def marketplaceView(request):
    return render(request, "marketplace.html", {})


@apiKeyRequired
def feedbackView(request):
    return render(request, "feedback.html", {})


def requestAuth(_request, provider):
    """
    Initiates an OAuth authentication request (Github, etc).

    @param {HttpRequest} request - The request object.
    @returns {HttpResponseRedirect} - A redirect response that navigates the user to OAuth
        authorization page.
    """
    clientID = ""
    authorization_url = ""
    providerScope = []
    _request.session["provider"] = provider

    if provider == "GitHub":
        clientID = os.getenv("GITHUB_CLIENT_ID")
        authorization_url = "https://github.com/login/oauth/authorize"
        providerScope = ["user"]

    elif provider == "Google":
        clientID = os.getenv("GOOGLE_CLIENT_ID")
        authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
        providerScope = [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ]
    else:
        raise AttributeError("Unsupported ouath provider")

    print(clientID)
    print(authorization_url)

    client = WAC(clientID)

    url = client.prepare_request_uri(
        authorization_url,
        redirect_uri=os.getenv("REDIRECT_URI"),
        scope=providerScope,
        state="test",
    )
    return HttpResponseRedirect(url)


class Callback(TemplateView):
    def get(self, _request):
        """
        Handles the callback after GitHub authentication, creates the user in the db if they
        don't exist, and retrieves the user's info and API key (generating it if it doesn't exist).
        It then saves the API key to the user's cookies so it can be sent to the API routes in
        future requests.

        @param request: The HTTP request object containing the callback data from GitHub or Google.
        @returns: The rendered index.html page with the API token set in the cookies.
        """
        print(self.request)
        data = self.request.GET
        authcode = data["code"]
        try:
            provider = self.request.session['provider']
        except:
            return redirect("/")

        # state = data["state"]

        # Get API token
        if provider == "GitHub":
            token_url = "https://github.com/login/oauth/access_token"
            clientID = os.getenv("GITHUB_CLIENT_ID")
            clientSecret = os.getenv("GITHUB_CLIENT_SECRET")
            username = "login"
            apiRequestURL = os.getenv("GITHUB_API_URL_user")

        elif provider == "Google":
            token_url = "https://accounts.google.com/o/oauth2/token"
            clientID = os.getenv("GOOGLE_CLIENT_ID")
            clientSecret = os.getenv("GOOGLE_CLIENT_SECRET")
            username = "name"
            apiRequestURL = os.getenv("GOOGLE_API_URL_userprofile")
        client = WAC(clientID)

        data = client.prepare_request_body(
            code=authcode,
            redirect_uri=os.getenv("REDIRECT_URI"),
            client_id=clientID,
            client_secret=clientSecret,
        )

        if provider == "Google":  # caters request and header to google specifications
            data = dict(urllib.parse.parse_qsl(data))
            response = requests.post(token_url, json=data, timeout=10)
            client.parse_request_body_response(response.text)
            header = {"Authorization": f"Bearer {client.token['access_token']}"}
        else:  # caters to GitHub specifications
            response = requests.post(token_url, data=data, timeout=10)
            client.parse_request_body_response(response.text)
            header = {"Authorization": f"token {client.token['access_token']}"}

        response = requests.get(apiRequestURL, headers=header, timeout=10)

        oauthUserInfo = response.json()

        # For Github, if user has no visible email, make second request for email
        if not oauthUserInfo.get("email"):
            response = requests.get(
                os.getenv("GITHUB_API_URL_email"), headers=header, timeout=10
            )
            oauthUserInfo["email"] = response.json()[0]["email"]

        # Create a user in our db if none exists
        if oauthUserInfo.get("username"):
            username = oauthUserInfo.get("username")
        else:
            username = oauthUserInfo.get("email").split("@")[0]

        userInfo, httpsCode = UsersAPIView.getAuthenticatedUser(
            {"email": oauthUserInfo.get("email")}
        )
        if httpsCode == status.HTTP_404_NOT_FOUND:
            try:
                names = oauthUserInfo.get("name", "").split()
            except:
                names = ["quayside", "user"]
            if not names:
                names = [""]

            userInfo, httpsCode = UsersAPIView.createUser(
                {
                    "email": oauthUserInfo.get("email"),
                    "username": username,
                    "firstName": names[0],
                    "lastName": names[-1],
                }
            )
            if httpsCode != status.HTTP_201_CREATED:
                print(f"User creation failed: {userInfo}")
                return HttpResponseServerError(f"An error occurred: {userInfo}")

        # Redirect instead of rendering (to make it update)
        response = redirect("/")

        apiToken = userInfo.get("apiKey")  # Get API key

        if apiToken:
            apiToken = decryptApiKey(apiToken)
        # Create an api key if it doesn't exist in the db yet
        else:
            # Create/encrypt API key
            apiToken = createEncodedApiKey(userInfo["id"])
            encryptedApiKey = encryptApiKey(apiToken)

            message, httpsCode = UsersAPIView.updateUser(
                {
                    "id": userInfo["id"],
                    "apiKey": encryptedApiKey,
                },
                apiToken,
            )
            if httpsCode != status.HTTP_200_OK:
                print(f"User update failed: {message}")
                return HttpResponseServerError(f"An error occurred: {message}")

        # Save api key to cookies
        # Setting httponly is safer and doesn't let the key be accessed by js (to prevent xxs).
        # Instead the browser will always pass the cookie to the server.
        response.set_cookie("apiToken", apiToken, httponly=True)

        # Make sure to add email not created already (oath doesn't require username I think but does require email)
        if "username" not in userInfo or not userInfo["username"]:
            message, httpsCode = UsersAPIView.updateUser(
                {
                    "id": userInfo["id"],
                    "username": username,
                },
                apiToken,
            )
            if httpsCode != status.HTTP_200_OK:
                print(f"User update failed: {message}")
                return HttpResponseServerError(f"An error occurred: {message}")

        return response
