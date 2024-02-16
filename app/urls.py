from django.urls import path

from . import views
from api.views.v1 import login

urlpatterns = [
    path('login/', login.login, name="login"),
    #path('callback/', login.Callback.as_view(), name='Callback'),
    path('create-project', views.createProject, name='create_project_view'),
    path('project/<str:projectID>/', views.project, name='project_view'),
    
]
