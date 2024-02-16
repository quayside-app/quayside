from django.urls import path

from . import views

urlpatterns = [
    path('create-project', views.createProjectView, name='create-project-view'),
    path('project/<str:projectID>/graph', views.projectGraphView, name='project-graph-view'),
    path('project/<str:projectID>/graph/task/<str:taskID>', views.taskView, name='task-detail-view'),
]
