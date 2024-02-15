from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Project
from api.serializers import ProjectSerializer
from rest_framework import status


class ProjectsAPIView(APIView):
    def get(self, request):
        """
        Retrieves a list of Project objects from MongoDB, filtered based on query parameters 
        provided in the request. 

        Query Parameters:
            - id (objectID str)
            - name (str)
            - types (list[str])
            - objectives (list[str])
            - startDate (date, 'YYYY-MM-DD')
            - endDate (date, 'YYYY-MM-DD')
            - budget (str)
            - assumptions (list[str])
            - scopesIncluded (list[str])
            - scopesExcluded (list[str])
            - risks (list[str])
            - userIDs (list[ObjectId])
            - projectManagerIDs (list[ObjectId])
            - sponsors (list[str])
            - contributorIDs (list[ObjectId])
            - completionRequirements (list[str])
            - qualityAssurance (list[str])
            - KPIs (list[str])
            - otherProjectDependencies (list[ObjectId])
            - informationLinks (list[str])
            - completionStatus (str)
            - teams (list[ObjectId])


        @return: A Response object containing a JSON array of serialized Project objects that 
        match the query parameters.

        @example:
            # Example request using query parameters for filtering projects by userID
            GET /api/v1/projects?userIDs=1234

        """
        try:
            #! TODO: Authentication
            query_params = request.query_params.dict()
            
            #! TODO: Filter query params to prevent injection attack?!!

            projects = Project.objects.filter(**query_params)  # Query mongo

            serializer = ProjectSerializer(projects, many=True)

            return Response(serializer.data)
        except:
            return Response({'message': 'Projects not found'}, status=404)

    def post(self, request):
        """
        Creates a project or list of projectss

        TODO MORE COMMENTS

        @return: A Response object with the created prject(s) data or an error message.
        """
        response_data, http_status = self.createProjects(request.data) 
        return Response(response_data, status=http_status)
    
    @staticmethod
    def createProjects(projectData):
        """
        Service API function that can be called internally as well as through the API to create tasks
        Creates a single task or multiple tasks based on the input data.

        @param task_data      Dict for a single project dict or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """

        #! TODO Authenticate
        if isinstance(projectData, list):
            serializer = ProjectSerializer(data=projectData, many=True)
        else:
            serializer = ProjectSerializer(data=projectData)

        if serializer.is_valid():
            serializer.save()  # Save the project(s) to the database
            return serializer.data, status.HTTP_201_CREATED  # Returns data including new primary key
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST

"""
TEST
http://127.0.0.1:8000/api/v1/tasks/?projectID=65530c4d3f9666ab932b59e2
"""