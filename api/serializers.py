from rest_framework_mongoengine.serializers import DocumentSerializer
#import serializers
from api.models import User, Project

class UserSerializer(DocumentSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'firstName', 'lastName', 'username', 'teamIDs']
        

class ProjectSerializer(DocumentSerializer):
    class Meta:
        model = Project
        # Default to all fields
