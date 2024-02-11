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

        Example:
            # Example request using query parameters for filtering projects by userID
            GET /api/projects?userIDs=1234

        """
        query_params = request.query_params.dict()
        
        #! TODO: Filter query params to prevent injection attack?!!

        projects = Project.objects.filter(**query_params)  # Query mongo

        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data)

