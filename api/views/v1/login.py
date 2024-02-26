from rest_framework.views import APIView

class  LoginAPIView(APIView):
    def get(self, request):
        query_params = request.query_params.dict()
        
    
        
        