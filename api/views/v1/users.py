from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.models import User
from api.serializers import UserSerializer


class UserDetailAPIView(APIView):
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
            user_id = request.GET.get('id') or None
            email = request.GET.get('email') or None

            if user_id and email:
                return Response({'message': 'Only user id or email needed. Hint: remove email=<> from the url'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = None
            if user_id:
                user = User.objects.filter(id=user_id).first()
            elif email:
                user = User.objects.filter(email=email).first()
            else:
                user = User.objects.filter(None)

            if not user:
                return Response({'message': 'User(s) not found.'}, status=status.HTTP_400_BAD_REQUEST)
            
            serialized_user = UserSerializer(user).data
            return Response({'user': serialized_user}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': f'Error getting user details: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        