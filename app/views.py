
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import NewProjectForm

def project(request, projectID):
    return render(request, 'project.html', {'project_ID': projectID})

def createProject(request):
    # If this is a POST request we need to process the form data
    if request.method == "POST":
        form = NewProjectForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            # TODO
            print(form.cleaned_data)

            # Redirect to home
            return HttpResponseRedirect("/")

    # If a GET (or any other method)  create a blank form
    else:
        form = NewProjectForm()

    return render(request, "newProjectModal.html", {"form": form})