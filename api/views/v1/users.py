from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.models import User
from api.serializers import UserSerializer


class UserDetailAPIView(APIView):

    def get(self, request):
        # TODO very very important!!!!!
        # add authentication.
        """
        Retrieves a single users information. User is found by query of id or email.
        Endpoint: 
            - GET /api/{version}/users/?id={user_id}
            - GET /api/{version}/users/?email={email}
        
        Query Parameters:
            - id (objectID str)
            - email (str)

        return: Basic information about a user.

        """
        try:
            user_id = request.GET.get('id')
            email = request.GET.get('email')

            if not user_id and not email:
                return Response({'message': 'User id or email required. Hint: /?id=<>'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user_id and email:
                return Response({'message': 'Only user id or email needed. Hint: remove /?email=<>'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user_id:
                user = User.objects.filter(id=user_id).first()
            else:
                user = User.objects.filter(email=email).first()

            if not user:
                return Response({'message': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
            
            serialized_user = UserSerializer(user).data
            return Response({'user': serialized_user}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': f'Error getting user details: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)