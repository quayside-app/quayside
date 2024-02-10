from django.urls import path

from . import views

urlpatterns = [
    path("/users/:username", views.index, name="index"),
]