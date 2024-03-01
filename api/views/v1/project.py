from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Project
from api.serializers import ProjectSerializer

from django.utils.decorators import method_decorator
from api.decorators import api_key_required

@method_decorator(api_key_required, name='dispatch')  # dispatch protects all HTTP requests coming in
class ProjectAPIView(APIView):
    def get(self, request, id):
        """
        Retrieves a Project object from MongoDB, filtered based on id provided in the URL path.

        Path Parameters:
            - id (str): The project ID of the project to retrieve.

        @return: A Response object containing a serialized Project object.
        """

        try:
            #! TODO: Authentication
            # TODO: Remove??
            #! TODO: Filter query params to prevent injection attack?!!
            project = Project.objects.get(id=id)

            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        except:
            return Response({'message': 'Project not found'}, status=404)