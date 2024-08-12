from rest_framework import serializers 
from .models import Status, Project 

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Status
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        # Default to all fields
