from django.urls import path

from . import views

urlpatterns = [
    path('create-project', views.createProject, name='create_project_view'),
    path('project/<str:projectID>/', views.project, name='project_view'),
    path('login/',views.login, name='login_view'),
    path('auth', views.RequestAuth, name ='authorize'),
    path('callback/', views.Callback.as_view(), name='callback'),
    path('user', views.user, name = 'user')
]
