
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import NewProjectForm
from api.views.v1.generatedTasks import GeneratedTasks
from api.views.v1.projects import ProjectsAPIView
from oauthlib.oauth2 import WebApplicationClient as WAC
import requests
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
import os
from django.views.generic.base import TemplateView

def login(request):
    return render(request, 'login.html')
 
def project(request, projectID):
    return render(request, 'project.html', {'project_ID': projectID})

def createProject(request):
    # If this is a POST request, process the form data
    if request.method == "POST":
        form = NewProjectForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            print(form.cleaned_data)
            name = form.cleaned_data["description"]

            projectData, _ = ProjectsAPIView.createProjects({"name": name, "userIDs": ["6521d8581bcf69b7d260608b"] }) #! TODO change to not-hardcoded
            projectID = projectData["id"]
            GeneratedTasks.generateTasks({"projectID": projectID, "name": name})

            # Redirect to home
            return HttpResponseRedirect(f"/project/{projectID}")

    # If a GET (or any other method), create a blank form
    else:
        form = NewProjectForm()

    return render(request, "newProjectModal.html", {"form": form})


def RequestAuth(request):
    clientID = os.getenv("GITHUB_CLIENT_ID")
    client = WAC(clientID)
    
    authorization_url = 'https://github.com/login/oauth/authorize'
    
    
    url = client.prepare_request_uri(
        authorization_url,
        redirectURL = 'http://127.0.0.1:8000/callback',
        scope =['user:email'],
        state = '/'
    )
    return HttpResponseRedirect(url)

class Callback(TemplateView):
    def get(self, request):
        data = self.request.GET
        authcode = data['code']
        state = data['state']
        print(authcode)
        print(state)
        
        #Get API token
        
        token_url = 'https://github.com/login/oauth/access_token'
        clientID = os.getenv("GITHUB_CLIENT_ID")
        clientSecret = os.getenv("GITHUB_CLIENT_SECRET")
        
        client = WAC(clientID)
        
        data = client.prepare_request_body(
            code = authcode,
            redirect_uri = 'http://127.0.0.1:8000/callback',
            client_id = clientID,
            client_secret = clientSecret
        )
        
        response = requests.post(token_url, data = data)
        
        client.parse_request_body_response(response.text)
        
        header = {'Authorization': 'token {}'.format(client.token['access_token'])}
        
        response = requests.get(os.getenv('GITHUB_API_URL'), headers=header)
        
        json_dict  = response.json()
        print(json_dict)
        return HttpResponseRedirect('http://127.0.0.1:8000')