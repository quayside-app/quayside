from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Task
from api.serializers import TaskSerializer


class TasksAPIView(APIView):
    def get(self, request):
        """
        Retrieves a list of Project objects from MongoDB, filtered based on query parameters 
        provided in the request. 

        Query Parameters:
            - parentTaskID (objectId str)
            - name (str)
            - objectives (list[str])
            - scopesIncluded (list[str])
            - scopesExcluded (list[str])
            - contributorIDs (list[objectId str])
            - otherProjectDependencies (list[objectId str])
            - otherTaskDependencies (list[objectId str])
            - projectID (objectId str)
            - description (str)
            - startDate (date, 'YYYY-MM-DD')
            - endDate (date, 'YYYY-MM-DD')


        @return: A Response object containing a JSON array of serialized Project objects that 
        match the query parameters.

        Example:
            # Example request using query parameters for filtering projects by userID
            GET /api/v1/tasks?projectID=1234

        """
        try:
            #! TODO: Authentication
            query_params = request.query_params.dict()
            
            #! TODO: Filter query params to prevent injection attack?!!

            projects = Task.objects.filter(**query_params)  # Query mongo

            serializer = TaskSerializer(projects, many=True)

            return Response(serializer.data)
        except:
            return Response({'message': 'Tasks not found'}, status=404)

