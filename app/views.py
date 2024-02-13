
from django.shortcuts import render

def project(request, projectID):
    return render(request, 'project.html', {'project_ID': projectID})