from rest_framework import serializers 
from .models import Profile 

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        # user = serializers.PrimaryKeyRelatedField(read_only=True)

        # extra_kwargs = {
        #     'user': {'read_only': True}  # Makes 'user' field read-only, i.e., not required during POST requests
        # }