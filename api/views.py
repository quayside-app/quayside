from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

import mongoengine as mongo
from dotenv import load_dotenv
import os

######### TODO: Move the following somewhere else??

def connect_database():
    # Load environment variables from .env file
    load_dotenv()
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    hostname = "quayside-cluster.ry3otj1.mongodb.net"
    database = "quayside"

    # For MongoEngine, the connection string is usually passed directly to the connect function
    
    connection_string = f"mongodb+srv://{username}:{password}@{hostname}/{database}?retryWrites=true&w=majority"
    
    # No good way to tell if connection exists besides this try/except
    try:
        mongo.get_connection(alias='default')
    except Exception as e:
        # If an exception is raised, no connection could be retrieved so create one
        mongo.connect(db=database, host=connection_string)

######### End TODO
    

class UserListView(APIView):
    """
    List all users.
    """

    def get(self, request, format=None):
        connect_database()
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post ():