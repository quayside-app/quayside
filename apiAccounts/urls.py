from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path(
        f"{settings.API_VERSION}/accounts/",
        views.ProfilesAPIView.as_view(),
        name=f"{settings.API_VERSION}-get-user",
    )
    
]

