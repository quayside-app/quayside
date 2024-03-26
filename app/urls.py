from django.urls import path

from . import views

urlpatterns = [
    path("create-project/", views.createProjectView, name="create-project-view"),
    path(
        "project/<str:projectID>/graph/",
        views.projectGraphView,
        name="project-graph-view",
    ),
    path(
        "project/<str:projectID>/graph/task/<str:taskID>",
        views.taskView,
        name="task-detail-view",
    ),
    path(
        "project/<str:projectID>/graph/create-task/<str:parentTaskID>",
        views.createTaskView,
        name="create-task-view",
    ),
    path("login/", views.userLogin, name="login_view"),
    path("auth/", views.requestAuth, name="authorize"),
    path("callback/", views.Callback.as_view(), name="callback"),
]
