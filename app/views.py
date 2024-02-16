
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import NewProjectForm, TaskForm
from api.views.v1.generatedTasks import GeneratedTasks
from api.views.v1.projects import ProjectsAPIView
from api.views.v1.tasks import TasksAPIView



def projectGraphView(request, projectID):
    return render(request, "graph.html", {"project_ID": projectID})

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


def createProjectView(request):
    
    # If this is a POST request, process the form data
    if request.method == "POST":
        form = NewProjectForm(request.POST)
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            name = form.cleaned_data["description"]

            projectData, _ = ProjectsAPIView.createProjects({"name": name, "userIDs": ["6521d8581bcf69b7d260608b"] }) #! TODO change to not-hardcoded
            projectID = projectData["id"]
            GeneratedTasks.generateTasks({"projectID": projectID, "name": name})

            # Redirect to project
            return HttpResponseRedirect(f"/project/{projectID}/graph")

    # If a GET (or any other method), create a blank form
    else:
        form = NewProjectForm()

    return render(request, "newProjectModal.html", {"form": form})