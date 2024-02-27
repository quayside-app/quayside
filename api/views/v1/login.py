from rest_framework.views import APIView
from api.models import User
from api.serializers import UserSerializer
class  LoginAPIView(APIView):
    def get(userData):
        query_params = {'email': userData['email']}
        
        user = User.objects.filter(**query_params)
        serializer = UserSerializer(user, many=True)
        print(serializer.data)
        
    
        
        