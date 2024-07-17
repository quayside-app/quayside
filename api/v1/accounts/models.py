from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# "Extends" User field
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    apiKey = models.CharField(blank=True) 
    image = models.URLField(blank=True)  # TODO: Check if this should be url

    def __str__(self):
        return f"{self.user.username}'s profile"