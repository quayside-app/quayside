from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import User
from api.serializers import UserSerializer


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
        print("serializer: ", serializer)
        if serializer.is_valid():
            user = User.objects.create(**serializer.validated_data)

            response_data = UserSerializer(user).data

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid input data.', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


"""
{
"email": "kaiverson@alaska.edu",
"username": "kaiverson"
}
"""