from django.urls import path

from app import views

urlpatterns = [
    path("create-project/", views.createProjectView, name="create-project-view"),
    path(
        "project/<str:projectID>/graph/",
        views.projectGraphView,
        name="project-graph-view",
    ),

    path(
        "project/<str:projectID>/graph/give-feedback",
        views.createTaskFeedback,
        name="task-feedback-form",
    ),
    path(
        "project/<str:projectID>/kanban/",
        views.projectKanbanView,
        name="project-kanban-view",
    ),
    path(
        "project/<str:projectID>/",
        views.editProjectView,
        name="project-detail-view",
    ),
    path(
        "project/<str:projectID>/<str:viewType>/task/<str:taskID>/",
        views.taskView,
        name="task-detail-view",
    ),
    path(
        "project/<str:projectID>/<str:viewType>/create-task/<str:parentTaskID>/",
        views.taskView,
        name="create-task-with-parent-view",
    ),
    path(
        "project/<str:projectID>/<str:viewType>/create-task/",
        views.taskView,
        name="create-task-tree-view",
    ),
    #path("login/", views.userLogin, name="login-view"),
    #path("logout/", views.userLogout, name="userLogout-view"),
    path("welcome/", views.logout, name="logout-view"),
    path("settings/", views.settingsView, name="settings-view"),
    path("invite/", views.inviteView, name="invite-view"),
    path("tutorial/", views.tutorialView, name="tutorial-view"),
    path("marketplace/", views.marketplaceView, name="marketplace-view"),
    path("feedback/", views.feedbackView, name="feedback-view"),
    path("auth/<str:provider>/", views.requestAuth, name="authorize"),
    path("callback/", views.Callback.as_view(), name="callback"),
    path('redirect/', views.redirectOffSite,name='offsite-redirect'),
]
