from django.urls import path, re_path

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
    path("login/", views.userLogin, name="login_view"),
    path("logout/", views.userLogout, name="logout_view"),
    path("welcome", views.logout, name="logout_view"),
    path("auth/<str:provider>", views.requestAuth, name="authorize"),
    path("callback/", views.Callback.as_view(), name="callback"),
    path('redirect/', views.redirectOffSite,name='offsite_redirect'),
    #re_path(r'^auth(?P<provider>)', views.requestAuth, name="authorize")
]
