from rest_framework import serializers
from .models import User

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=100)
    firstName = serializers.CharField(max_length=100, allow_blank=True, required=False)
    lastName = serializers.CharField(max_length=100, allow_blank=True, required=False)
    teamIDs = serializers.ListField(child=serializers.CharField(), required=False)

