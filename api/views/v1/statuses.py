from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.decorators import apiKeyRequired
from api.serializers import ProjectSerializer
from api.views.v1.projects import ProjectsAPIView
from api.utils import getAuthorizationToken


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
                - projectId (objectID str)

        @return A Response object containing a JSON array of serialized Status objects that
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
        Creates a status. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body can contain:
                - projectID (objectID str) [REQUIRED]
                - name (str) [REQUIRED]
                - color (str) optional, defaults to "323232"
                - order (int) optional, defaults to max+1

        @return A response telling you if the status was created.

        @example javascript:
            fetch('quayside.app/api/v1/statuses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "projectID": "5AC9942376", "name": "Backlog", "color": "4A90E2" }),
            });
        """
        responseData, httpStatus = self.createStatus(
            request.data.copy(), getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def put(self, request):
        """
        Updates a single status (partial update — supply only the fields you want to change).
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body MUST contain:
                - projectID (objectID str)
                - id (objectID str)
            Optional fields:
                - name (str)
                - color (str)

        @return: A Response object with the updated status data or an error message.

        @example javascript
            await fetch(`/api/v1/statuses/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({ "projectID": "5AC9942376", "id": "abc123", "color": "FF0000" }),
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
                - projectID (objectID str) [REQUIRED]

        @return: A Response object with a success or an error message.

        @example javascript:
            fetch(`/api/v1/statuses/?id=1234&projectID=5678`, {
                method: 'DELETE',
            });
        """
        responseData, httpStatus = self.deleteStatus(
            request.query_params, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    @staticmethod
    def getStatuses(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to get
        project data based on input data.

        @param statusData       Dict with 'projectID'.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": statusData["projectID"]}, authorizationToken
            )
            data = data[0]

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return {"message": data.get("message", "Error")}, httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return {"message": "No status associated with project"}, status.HTTP_404_NOT_FOUND

            return data["taskStatuses"], status.HTTP_200_OK
        except Exception as e:
            print("Error:", e)
            return {"message": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def updateStatus(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to update
        a status. Supports partial updates: only fields present in statusData are changed.

        @param statusData   Dict with 'projectID', 'id', and any subset of 'name', 'color'.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": statusData["projectID"]}, authorizationToken
            )
            data = data[0]

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return {"message": data.get("message", "Error")}, httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return {"message": "Status not found."}, status.HTTP_404_NOT_FOUND

            for stat in data["taskStatuses"]:
                if str(stat["id"]) == str(statusData["id"]):
                    if "name" in statusData:
                        stat["name"] = statusData["name"].strip()
                    if "color" in statusData:
                        stat["color"] = statusData["color"].upper()

                    serializer = ProjectSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return {"message": "Successfully updated status"}, status.HTTP_200_OK
                    return {"message": str(serializer.errors)}, status.HTTP_400_BAD_REQUEST

            return {"message": "Status not found."}, status.HTTP_404_NOT_FOUND

        except Exception as e:
            print("Error:", e)
            return {"message": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def createStatus(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to create
        a status.

        @param statusData   Dict with 'projectID', 'name', and optionally 'color', 'order'.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": statusData["projectID"]}, authorizationToken
            )
            data = data[0]

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return {"message": data.get("message", "Error")}, httpsCode

            if "taskStatuses" not in data:
                data["taskStatuses"] = []

            # Case-insensitive duplicate name check
            new_name = statusData.get("name", "").strip()
            for stat in data["taskStatuses"]:
                if stat["name"].lower() == new_name.lower():
                    return {"message": "A column with this name already exists."}, status.HTTP_409_CONFLICT

            # Default color
            if not statusData.get("color"):
                statusData["color"] = "323232"
            statusData["color"] = statusData["color"].upper()

            # Default order = max existing order + 1
            if statusData.get("order") is None:
                max_order = max((s["order"] for s in data["taskStatuses"]), default=0)
                statusData["order"] = max_order + 1

            statusData["name"] = new_name
            statusData.pop("projectID", None)
            data["taskStatuses"].append(statusData)

            serializer = ProjectSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return {"message": "Successfully created status"}, status.HTTP_201_CREATED
            return {"message": str(serializer.errors)}, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            print("Error:", e)
            return {"message": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def deleteStatus(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to delete
        a status. Recompacts order values of remaining statuses after deletion.

        @param statusData   Dict (or QueryDict) with 'id' and 'projectID'.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": statusData["projectID"]}, authorizationToken
            )
            data = data[0]

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return {"message": data.get("message", "Error")}, httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return {"message": "Status not found."}, status.HTTP_404_NOT_FOUND

            original_len = len(data["taskStatuses"])
            data["taskStatuses"] = [
                s for s in data["taskStatuses"] if str(s["id"]) != str(statusData["id"])
            ]

            if len(data["taskStatuses"]) == original_len:
                return {"message": "Status not found."}, status.HTTP_404_NOT_FOUND

            # Recompact order values to [1, 2, 3, ...]
            for i, stat in enumerate(
                sorted(data["taskStatuses"], key=lambda s: s["order"]), start=1
            ):
                stat["order"] = i

            serializer = ProjectSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return {"message": "Successfully deleted status"}, status.HTTP_200_OK
            return {"message": str(serializer.errors)}, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            print("Error:", e)
            return {"message": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
