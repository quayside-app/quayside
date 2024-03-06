from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mongoengine.errors import NotUniqueError

from django.utils.decorators import method_decorator

from api.models import User
from api.serializers import UserSerializer
from api.decorators import apiKeyRequired


# dispatch protects all HTTP requests coming in
@method_decorator(apiKeyRequired, name="dispatch")
class UsersAPIView(APIView):
    """
    Create, get, and update users.
    """

    def get(self, request):
        """
        Retrieves user information based on optional query parameters. If no parameters are provided,
        retrieves a list of all users. Supports filtering by user ID or email address.
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The query parameters can be:
                - id (objectID str): Filter users by ID.
                - email (str): Filter users by email address.

        @return A Response object containing a JSON array of serialized user objects that match the query parameters.
        If no users match the query, a 400 Bad Request response is returned.

        @example Javascript:
            // To fetch all users
            fetch('/api/v1/users');

            // To fetch a user by ID
            fetch('/api/v1/users?id=1234');

            // To fetch a user by email
            fetch('/api/v1/users?email=user@example.com');
        """

        try:
            queryParams = request.query_params.dict()

            responseData, httpStatus = self.getUser(queryParams)

            return Response(responseData, httpStatus)

        except Exception as e:
            return Response(
                {"message": f"Error getting user details: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """
        Handles the POST request to create a new user based on the provided body parameters.
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            Headers:
                - Content-Type: 'application/json'
            Body parameters:
                - email (str) [REQUIRED]: The email address of the user.
                - firstName (str): The first name of the user.
                - lastName (str): The last name of the user.
                - username (str) [REQUIRED]: The username for the user.
                - teamIDs (list[str]): List of team IDs the user is associated with.

        @return {HttpResponse} - On success, returns a status of 200 and a JSON body containing the user's details.


        @example JavaScript:
            fetch('quayside.app/api/v1/users/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: 'user@example.com',
                    firstName: 'John',
                    lastName: 'Doe',
                    username: 'johndoe',
                    teamIDs: ['team1', 'team2']
                })
            });
        """
        if request.content_type != "application/json":
            return Response(
                {"error": "Invalid Content-Type. Use application/json."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        responseData, httpStatus = self.createUser(request.data)

        return Response(responseData, httpStatus)

    def put(self, request):
        """
        Updates a single user.
        Requires 'apiToken' passed in auth header or cookies.


        @param {HttpRequest} request - The request object.
                @param {HttpRequest} request - The request object.
            The request body can contain:
                - id (str) [REQUIRED]
                - email (str): The email address of the user.
                - firstName (str): The first name of the user.
                - lastName (str): The last name of the user.
                - username (str) : The username for the user.
                - teamIDs (list[str]): List of team IDs the user is associated with.


        @return: A Response object with the updated task data or an error message.

        @example javascript
            await fetch(`quayside.app/api/v1/users/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({id: '1234, name: 'Task2'},
            });

        """
        responseData, httpStatus = self.updateUser(request.data)
        return Response(responseData, status=httpStatus)

    @staticmethod
    def updateUser(userData):
        """
        Service API function that can be called internally as well as through the API to update
        a user based on input data.

        @param task_data      Dict for a single project dict or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
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

        return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def getUser(userData):
        """
        Service API function that can be called internally as well as through the API to get a user

        @param userData      Dict of data for a single user.
        @return      A tuple of (response_data, http_status).
        """

        user_id = userData.get("id") or None
        email = userData.get("email") or None

        if user_id and email:
            return {
                "message": "Only user id or email needed. Hint: remove email=<> from the url"
            }, status.HTTP_400_BAD_REQUEST

        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif email:
            user = User.objects.filter(email=email).first()
        else:
            user = User.objects.filter(None)

        if not user:
            return {"message": "User(s) not found."}, status.HTTP_400_BAD_REQUEST

        serialized_user = UserSerializer(user).data
        return {"user": serialized_user}, status.HTTP_200_OK

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
            if "email" in error_message:
                return {
                    "error": "Email address is already in use."
                }, status.HTTP_400_BAD_REQUEST
            #           elif 'username' in error_message:
            #               return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

            return {
                "error": "Duplicate key error.",
                "details": error_message,
            }, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            return {
                "error": "Internal server error.",
                "details": str(e),
            }, status.HTTP_500_INTERNAL_SERVER_ERROR
