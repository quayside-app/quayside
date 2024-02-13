
from django.shortcuts import render

def project(request, projectID):
    return render(request, 'project.html', {'project_ID': projectID})

def create_project(request):
    return render(request, 'createProjectModal.html', )