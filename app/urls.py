from django.urls import path

from . import views

urlpatterns = [
    path('create-project', views.createProject, name='create_project_view'),
    path('project/<str:projectID>/', views.project, name='project_view'),
]
