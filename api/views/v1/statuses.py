from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from api.decorators import apiKeyRequired
from api.serializers import ProjectSerializer
from api.views.v1.tasks import TasksAPIView
from api.models import Project
from api.utils import getAuthorizationToken, decodeApiKey
from api.views.v1.projects import ProjectsAPIView


@method_decorator(
    apiKeyRequired, name="dispatch"
)  # dispatch protects all HTTP requests coming in
class StatusesAPIView(APIView):
    """
    Create, get, and update a project status.
    """

    def get(self, request):
        """
        Retrieves a list of Status objects for a Project from MongoDB, filtered based on query parameters
        provided in the request. Requires 'apiToken' passed in auth header or cookies. Only gets
        projects where UserID matches.

        @param {HttpRequest} request - The request object.
            The query parameters can be:
                - id (objectID str)
                - name (str)
                - color (str)
                - order (str)

        @return A Response object containing a JSON array of serialized Project objects that
        match the query parameters.

        @example Javascript:
            fetch('quayside.app/api/v1/statuses?projectID=1234');
        """
        responseData, httpStatus = self.getStatuses(
            request.query_params.dict(), getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def post(self, request):
        """
        Creates status(es). Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body can contain:
                - id (objectID str)
                - name (str)
                - color (str)
                - order (str)
        @param {str} authorizationToken - JWT authorization token.

        @return A Response object containing a JSON array of the created project.

        @example javascript:

            fetch('quayside.app/api/v1/statuses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "name":  "backlog", "color": "A4279", "order":  2 }),
            });

        """
        responseData, httpStatus = self.createProjects(
            request.data, getAuthorizationToken(request)
        )
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
                - color (str)
                - order (str)
        @return: A Response object with the updated task data or an error message.

        @example javascript
            await fetch(`/api/v1/statuses?id=1234`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({ "name":  "backlog", "color": "A4279", "order":  2 }),
            });

        """
        responseData, httpStatus = self.updateStatus(
            request.data, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def delete(self, request):
        """
        Deletes a status from a project. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The query parameters MUST be:
                - id (objectID str) [REQUIRED]

        @return: A Response object with a success or an error message.

        @example javascript:

            fetch(`/api/v1/statuses?id=1234`, {
                method: 'DELETE',
            });
        """

        responseData, httpStatus = self.deleteStatus(
            request.query_params, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    @staticmethod
    def getStatuses(projectData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to get
        project data based on input data.

        @param projectData      Dict for a single project.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """

        try:
            # Only get project where user is a contributor
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": projectData["id"]}, authorizationToken
            )

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return data["message"], httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return { "message": "No status associated with project" }, status.HTTP_404_NOT_FOUND

            return data["taskStatuses"], status.HTTP_200_OK
        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def updateStatus(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to update
        project data based on input data.

        @param projectData      Dict for a single project.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """

        try:
            # Only get project where user is a contributor
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": statusData["projectID"]}, authorizationToken
            )

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return data["message"], httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return {
                    "message": "No status associated with project"
                }, status.HTTP_204_NO_CONTENT
            
            for stat in data["taskStatuses"]:
                if stat["id"] == statusData["id"]:
                    stat = statusData.pop("projectID")
                    serializer = ProjectSerializer(data=data)

                    if serializer.is_valid():
                        serializer.save()  # Updates projects
                        return {"message": "Successfully updated status"}, status.HTTP_200_OK

                    return serializer.errors, status.HTTP_400_BAD_REQUEST

            return {"message": "Failed to update status"}, status.HTTP_200_OK
        
        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def createStatus(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to create
        project(s) based on input data.

        @param projectData      Dict for a single project dict or list of dicts for multiple tasks.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:
            # Only get project where user is a contributor
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": statusData["projectID"]}, authorizationToken
            )

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return data["message"], httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return {
                    "message": "No status associated with project"
                }, status.HTTP_204_NO_CONTENT
            
            for stat in data["taskStatuses"]:
                if stat["name"] == statusData["name"]:
                    return {
                        "message": "Status with name already exists"
                    }, status.HTTP_403_FORBIDDEN

            data["taskStatuses"].append(statusData.pop("projectID"))
            serializer = ProjectSerializer(data=data)

            if serializer.is_valid():
                serializer.save()  # Updates projects
                return {"message":"Successfully created status"}, status.HTTP_200_OK
            
            return {"message":serializer.errors}, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def deleteStatus(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to delete
        project and all associated tasks.

        @param projectData      Dict for a single project
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:
            # Only get project where user is a contributor
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": statusData["projectID"]}, authorizationToken
            )

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return data["message"], httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return {
                    "message": "No status associated with project"
                }, status.HTTP_204_NO_CONTENT
            
            taskFound = False
            for i, stat in enumerate(data["taskStatuses"]):
                if stat["id"] == statusData["id"]:
                    data["taskStatuses"].pop(i)
                    taskFound = True
                    break

            if not taskFound:
                return { "message": "No status associated with project" }, status.HTTP_404_NOT_FOUND

            serializer = ProjectSerializer(data=data)

            if serializer.is_valid():
                serializer.save()  # Updates projects
                return {"message":"Successfully deleted status"}, status.HTTP_200_OK
            
            return {"message":serializer.errors}, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR
