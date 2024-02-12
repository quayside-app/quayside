from django.urls import path

from . import views

urlpatterns = [
    path('project/<str:projectID>/', views.project, name='project_view'),
]
