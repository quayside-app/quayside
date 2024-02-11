from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import User, Project

class UserSerializer(DocumentSerializer):
    class Meta:
        model = User
        # Default to all fields
        

class ProjectSerializer(DocumentSerializer):
    class Meta:
        model = Project
        # Default to all fields
