from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Project
from api.serializers import ProjectSerializer


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


"""
TEST
http://127.0.0.1:8000/api/v1/tasks/?projectID=65530c4d3f9666ab932b59e2
"""