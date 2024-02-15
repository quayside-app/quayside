from django.urls import path

from . import views

urlpatterns = [
    path('create-project', views.createProject, name='create-project-view'),
    path('project/<str:projectID>/graph', views.projectGraph, name='project-graph-view'),
]
