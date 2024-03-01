from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.models import User
from api.serializers import UserSerializer
from mongoengine.errors import NotUniqueError

from django.utils.decorators import method_decorator
from api.decorators import api_key_required

@method_decorator(api_key_required, name='dispatch')  # dispatch protects all HTTP requests coming in
class UsersAPIView(APIView):
    """
    User Detail API View

    Retrieves user information based on optional query parameters. If no parameters are provided,
    retrieves a list of all users. Supports filtering by user ID or email address.

    Endpoints:
    - GET /api/{version}/users/            (Retrieve a list of all users)
    - GET /api/{version}/users/?id={user_id}   (Retrieve a specific user by ID)
    - GET /api/{version}/users/?email={email}  (Retrieve a specific user by email)

    Query Parameters:
    - id (objectID str): Filter users by ID.
    - email (str): Filter users by email address.

    Response:
    - Returns basic information about the user or a list of users.
    - If no users match the query, a 400 Bad Request response is returned.

    Note:
    - To retrieve a specific user, provide either 'id' or 'email' as a query parameter.
    - To retrieve all users, make the request without any query parameters.

    """
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO very very important!!!!!
        # add authentication.
        try:
            queryParams = request.query_params.dict()

            responseData, httpStatus = self.getUser(queryParams)

            return Response(responseData, httpStatus)
        
        except Exception as e:
            return Response({'message': f'Error getting user details: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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

        responseData, httpStatus = self.createUser(request.data)

        return Response(responseData, httpStatus)
    def put(self, request):
        """
        Updates single user

        TODO comment
        TODO TEST
        """
        responseData, httpStatus = self.updateUser(request.data)
        return Response(responseData, status=httpStatus)
    
    @staticmethod
    def updateUser(userData):
        """
        TODO commentss
        """
        if "id" not in userData:
            return "Error: Parameter 'id' required", status.HTTP_400_BAD_REQUEST

        try:
            task = User.objects.get(id=userData["id"])
        except User.DoesNotExist:
            return None, status.HTTP_404_NOT_FOUND 

       
        serializer = UserSerializer(data=userData, instance=task, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates users
            return serializer.data, status.HTTP_200_OK
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST
        
    @staticmethod
    def getUser(userData):
        """
        Service API function that can be called internally as well as through the API to get a user

        @param userData      Dict of data for a single user.
        @return      A tuple of (response_data, http_status).
        """

        user_id = userData.get('id') or None
        email = userData.get('email') or None

        if user_id and email:
            return {'message': 'Only user id or email needed. Hint: remove email=<> from the url'}, status.HTTP_400_BAD_REQUEST
        
        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif email:
            user = User.objects.filter(email=email).first()
        else:
            user = User.objects.filter(None)

        if not user:
            return {'message': 'User(s) not found.'}, status.HTTP_400_BAD_REQUEST
        
        serialized_user = UserSerializer(user).data
        return {'user': serialized_user}, status.HTTP_200_OK
    
    @staticmethod
    def createUser(userData):
        """
        Service API function that can be called internally as well as through the API to create a user

        @param userData      Dict of data for a single user.
        @return      A tuple of (response_data, http_status).
        """

        serializer = UserSerializer(data=userData)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(**serializer.validated_data)
            response_data = UserSerializer(user).data
            return response_data, status.HTTP_201_CREATED
        
        except NotUniqueError as e:
            error_message = str(e)
            if 'email' in error_message:
                return {'error': 'Email address is already in use.'}, status.HTTP_400_BAD_REQUEST
#           elif 'username' in error_message:
#               return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return {'error': 'Duplicate key error.', 'details': error_message}, status.HTTP_400_BAD_REQUEST
             
        except Exception as e:
            return  {'error': 'Internal server error.', 'details': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    
       
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

"""TESTING
http://127.0.0.1:8000/api/v1/users/?email=schromya@gmail.com
"""