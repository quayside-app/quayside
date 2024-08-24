from rest_framework import serializers 
from .models import Status, Project 

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        # Default to all fields


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Status
        fields = '__all__'