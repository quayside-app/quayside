from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.decorators import apiKeyRequired
from api.serializers import ProjectSerializer
from api.views.v1.tasks import TasksAPIView
from api.models import Project
from django.core.exceptions import ObjectDoesNotExist 
from api.utils import getAuthorizationToken, decodeApiKey

from bson.objectid import ObjectId


@method_decorator(
    apiKeyRequired, name="dispatch"
)  # dispatch protects all HTTP requests coming in
class ProjectsAPIView(APIView):
    """
    Create, get, and update your project.
    """

    def get(self, request):
        """
        Retrieves a list of Project objects from MongoDB, filtered based on query parameters
        provided in the request. Requires 'apiToken' passed in auth header or cookies. Only gets
        projects where UserID matches.

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

        @example Javascript:
            fetch('quayside.app/api/v1/projects?userIDs=1234');
        """
        responseData, httpStatus = self.getProjects(
            request.query_params.dict(), getAuthorizationToken(request))
        return Response(responseData, status=httpStatus)

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
        @param {str} authorizationToken - JWT authorization token.

        @return A Response object containing a JSON array of the created project.

        @example javascript:

            fetch('quayside.app/api/v1/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'New Project' }),
            });

        """
        responseData, httpStatus = self.createProjects(request.data, getAuthorizationToken(request))
        return Response(responseData, status=httpStatus)

    def put(self, request):
        """
        Updates a single project.
        Requires 'apiToken' passed in auth header or cookies.


        @param {HttpRequest} request - The request object.
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
        @return: A Response object with the updated task data or an error message.

        @example javascript
            await fetch(`/api/v1/project/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({id: '1234, name: 'Project1'},
            });

        """
        responseData, httpStatus = self.updateProject(request.data, getAuthorizationToken(request))
        return Response(responseData, status=httpStatus)

    def delete(self, request):
        """
        Deletes a project or list of projects. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The query parameters MUST be:
                - id (objectID str) [REQUIRED]

        @return: A Response object with a success or an error message.

        @example javascript:

            fetch(`/api/v1/projects?id=1234`, {
                method: 'DELETE',
            });
        """

        responseData, httpStatus = self.deleteProjects(request.query_params, getAuthorizationToken(request))
        return Response(responseData, status=httpStatus)

    @staticmethod
    def getProjects(projectData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to get
        project data based on input data.

        @param projectData      Dict for a single project.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:

            # Only get project where user is a contributor
            userID = decodeApiKey(authorizationToken).get("userID")
            if "userIDs" not in projectData:
                projectData["userIDs"] = [userID]
            elif isinstance(projectData["userIDs"], list) and  userID not in  projectData["userIDs"]:
                projectData["userIDs"].append(userID)
            elif userID != projectData["userIDs"]:
                projectData["userIDs"] = [userID,  projectData["userIDs"]]

            projects = Project.objects.filter(**projectData)  # Query mongo

            if not projects:
                return {"message": "No projects were found or you do not have authorization."}, status.HTTP_400_BAD_REQUEST
            serializer = ProjectSerializer(projects, many=True)

            return serializer.data, status.HTTP_200_OK
        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def updateProject(projectData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to update
        project data based on input data.

        @param projectData      Dict for a single project.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        if "id" not in projectData:
            return "Error: Parameter 'id' required", status.HTTP_400_BAD_REQUEST

        try:
            project = Project.objects.get(id=projectData["id"])
        except ObjectDoesNotExist:
            return "Project not found", status.HTTP_404_NOT_FOUND
        
        # Check if userID is in the project's list of UserIDs
        userID = decodeApiKey(authorizationToken).get("userID")
        if ObjectId(userID) not in project["userIDs"]:  # Assuming 'user_ids' is the field name
            return {"message": "User not authorized for this project"}, status.HTTP_403_FORBIDDEN

        serializer = ProjectSerializer(
            data=projectData, instance=project, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates projects
            return serializer.data, status.HTTP_200_OK

        return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def createProjects(projectData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to create
        project(s) based on input data.

        @param projectData      Dict for a single project dict or list of dicts for multiple tasks.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        userID = decodeApiKey(authorizationToken).get("userID")
        if "userIDs" not in projectData or projectData["userIDs"] != [userID]:
            return {"message": "Request data must contain a list of userIDs with only your user ID present."}, status.HTTP_400_BAD_REQUEST

        if isinstance(projectData, list):
            serializer = ProjectSerializer(data=projectData, many=True)

        else:
            serializer = ProjectSerializer(data=projectData)

        if serializer.is_valid():
            serializer.save()  # Save the project(s) to the database
            # Returns data including new primary key
            return serializer.data, status.HTTP_201_CREATED

        return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def deleteProjects(projectData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to delete
        project and all associated tasks.

        @param projectData      Dict for a single project
        @return      A tuple of (response_data, http_status).
        """
        print("HHERE1")
        if "id" not in projectData:
            return {"message": "Parameter 'id' required"}, status.HTTP_400_BAD_REQUEST
        id = projectData["id"]
        print("HHERE2")
        project= Project.objects.get(id=id)
        print(project)

        userID = decodeApiKey(authorizationToken).get("userID")
        if ObjectId(userID) not in project["userIDs"]:
            return {"message": "Not authorized to delete project."}, status.HTTP_401_UNAUTHORIZED


        TasksAPIView.deleteTasks({"projectID": id})

        numberObjectsDeleted = project.delete()
        if numberObjectsDeleted == 0:
            return "No project found to delete.", status.HTTP_404_NOT_FOUND

        return "Project Deleted Successfully", status.HTTP_200_OK
    


