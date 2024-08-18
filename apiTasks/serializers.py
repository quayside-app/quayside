from rest_framework import serializers
from api.models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        # Default to all fields

class GeneratedTaskSerializer(serializers.Serializer):
    projectID = serializers.CharField(required=True)
    name = serializers.CharField(required=True)  # project name
    description = serializers.CharField(allow_blank=True, allow_null=True)
