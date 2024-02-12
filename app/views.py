
from django.shortcuts import render

def project(request, projectID):
    return render(request, 'project.html', {'projectID': projectID})