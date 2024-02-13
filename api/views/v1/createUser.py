from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import User
from api.serializers import UserSerializer
from mongoengine.errors import NotUniqueError


class CreateUserAPIView(APIView):
    def post(self, request):
        # TODO: finish filling this out. Don't really know what i'm doing.
        """
        Handles a request to create a new user based on body parameters.
        endpoint: POST /api/{version}/users/create

        @request
        Headers:
            - Content-Type: 'application/json'
        Body:
            - email (str) REQUIRED
            - firstName (str)
            - lastName (str)
            - username (str) REQUIRED
            - teamIDs (list[str])

        @response'
        Status 200
        Body:
            - email (str)
            - firstName (str)
            - lastName (str)
            - username (str)
            - teamIDs (list[str])
        """
        if request.content_type != 'application/json':
            return Response({'error': 'Invalid Content-Type. Use application/json.'}, status=status.HTTP_400_BAD_REQUEST)     

        serializer = UserSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(**serializer.validated_data)
            response_data = UserSerializer(user).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except NotUniqueError as e:
            error_message = str(e)
            if 'email' in error_message:
                return Response({'error': 'Email address is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            elif 'username' in error_message:
                return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Duplicate key error.', 'details': error_message}, status=status.HTTP_400_BAD_REQUEST)
             
        except Exception as e:
            return Response({'error': 'Internal server error.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Sample data I was using to test the route.
# Definitely need to learn how to do this in a test file.
"""
{
"email": "kaiverson@alaska.edu",
"username": "kaiverson",
"firstName": "Kai",
"lastName": "Iverson"
}
"""