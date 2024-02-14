from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from api.models import User, Project, Task


class UserSerializer(DocumentSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'firstName',
                  'lastName', 'username', 'teamIDs']


class ProjectSerializer(DocumentSerializer):
    class Meta:
        model = Project
        # Default to all fields


class TaskSerializer(DocumentSerializer):
    class Meta:
        model = Task
        # Default to all fields


class GeneratedTaskSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
