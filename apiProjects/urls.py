from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path(
        f"{settings.API_VERSION}/projects/",
        views.ProjectsAPIView.as_view(),
        name=f"{settings.API_VERSION}-projects-list",
    ),
    path(
        f"{settings.API_VERSION}/statuses/",
        views.StatusesAPIView.as_view(),
        name=f"{settings.API_VERSION}-statuses",
    )
]

