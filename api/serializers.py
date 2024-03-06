from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from api.models import User, Project, Task


class UserSerializer(DocumentSerializer):
    class Meta:
        model = User
        # Default to all fields


class ProjectSerializer(DocumentSerializer):
    class Meta:
        model = Project
        # Default to all fields


class TaskSerializer(DocumentSerializer):
    class Meta:
        model = Task
        # Default to all fields


class GeneratedTaskSerializer(serializers.Serializer):
    projectID = serializers.CharField(required=True)
    name = serializers.CharField(required=True)  # project name
