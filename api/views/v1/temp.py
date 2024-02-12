from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

class TempDetailAPIView(APIView):
    def get(self, request, temp):
        # You can customize the response message as needed
        response_data = {
            "message": f"Hello temp {temp}, you are using API v1"
        }
        return Response(response_data)