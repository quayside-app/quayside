from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Project
from api.serializers import ProjectSerializer
from api.views.v1.tasks import TasksAPIView
from rest_framework import status
from django.utils.decorators import method_decorator
from api.decorators import apiKeyRequired

@method_decorator(apiKeyRequired, name='dispatch')  # dispatch protects all HTTP requests coming in
class ProjectsAPIView(APIView):
    """
    Create, get, and update your project.
    """
    def get(self, request):
        """
        Retrieves a list of Project objects from MongoDB, filtered based on query parameters 
        provided in the request. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The query parameters can be:
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


        @return A Response object containing a JSON array of serialized Project objects that 
        match the query parameters.

        @example Javacript:
            // GET request using query parameters for filtering projects by userID
            fetch('quayside.app/api/v1/projects?userIDs=1234');
        """

        try:
            queryParams = request.query_params.dict()
            projects = Project.objects.filter(**queryParams)  # Query mongo
            serializer = ProjectSerializer(projects, many=True)

            return Response(serializer.data)
        except:
            return Response({'message': 'Projects not found'}, status=404)

    def post(self, request):
        """
        Creates project(s). Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body can contain:
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


        @return A Response object containing a JSON array of the created project.

        @example javascript:

            fetch('quayside.app/api/v1/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'New Project' }),
            });

        """
        responseData, httpStatus = self.createProjects(request.data)
        return Response(responseData, status=httpStatus)

    def delete(self, request):
        """
        Deletes a project or list of projects. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The query parameters MUST be:
                - id (objectID str)

        @return: A Response object with a success or an error message.

        @example javascript:

            fetch(`/api/v1/projects?id=${projectID}`, {
                method: 'DELETE',
            });
        """

        responseData, httpStatus = self.deleteProjects(request.query_params)
        return Response(responseData, status=httpStatus)

    @staticmethod
    def createProjects(projectData):
        """
        Service API function that can be called internally as well as through the API to create
        project(s) based on input data.

        @param task_data      Dict for a single project dict or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """

        if isinstance(projectData, list):
            serializer = ProjectSerializer(data=projectData, many=True)
        else:
            serializer = ProjectSerializer(data=projectData)

        if serializer.is_valid():
            serializer.save()  # Save the project(s) to the database
            # Returns data including new primary key
            return serializer.data, status.HTTP_201_CREATED
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def deleteProjects(projectData):
        """
        Service API function that can be called internally as well as through the API to delete
        project(s) and all associated tasks.
        
        @param projectData      Dict for a single project dict or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """

        # Check
        if "id" not in projectData:
            return "Error: Parameter 'id' required", status.HTTP_400_BAD_REQUEST

        id = projectData["id"]

        # Delete associated tasks
        ids = id
        if not isinstance(id, list):
            ids = [ids]

        for id in ids:
            result = TasksAPIView.deleteTasks({"projectID": id})

        numberObjectsDeleted = Project.objects(id=id).delete()
        if numberObjectsDeleted == 0:
            return "No project(s) found to delete.", status.HTTP_404_NOT_FOUND

        return "Project(s) Deleted Successfully", status.HTTP_200_OK

