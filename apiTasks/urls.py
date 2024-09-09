from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path(
        f"{settings.API_VERSION}/tasks/",
        views.TasksAPIView.as_view(),
        name=f"{settings.API_VERSION}-tasks",
    ),
    path(
        f"{settings.API_VERSION}/generatedTasks/",
        views.GeneratedTasksAPIView.as_view(),
        name=f"{settings.API_VERSION}-generatedTasks",
    ),


]

