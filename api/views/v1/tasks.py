from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from django.utils.decorators import method_decorator

from api.models import Task, Project
from api.serializers import TaskSerializer
from api.decorators import apiKeyRequired
from api.utils import getAuthorizationToken, decodeApiKey


# dispatch protects all HTTP requests coming in
@method_decorator(apiKeyRequired, name="dispatch")
class TasksAPIView(APIView):
    """
    Create, get, update, and delete tasks.
    """

    def get(self, request):
        """
        Retrieves a list of Project objects from MongoDB, filtered based on query parameters
        provided in the request. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            Query Parameters:
                - id (objectId str)
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
                - status (str)


        @return: A Response object containing a JSON array of serialized Task objects that
        match the query parameters.

        @example Javascript:
            fetch('quayside.app/api/v1/tasks?parentTaskID=1234');
        """

        responseData, httpStatus = self.getTasks(
            request.query_params.dict(), getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def post(self, request):
        """
        Creates a single task or a list of tasks.
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body can contain:
                - parentTaskID (objectId str) [REQUIRED]
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
                - status (str)

        @return: A Response object with the created task(s) data or an error message.

        @example Javascript:

            fetch('quayside.app/api/v1/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ parentTaskID: '1234',  name:'mya'}),
            });
        """
        responseData, httpStatus = self.createTasks(
            request.data, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def put(self, request):
        """
        Updates a single task.
        Requires 'apiToken' passed in auth header or cookies.


        @param {HttpRequest} request - The request object.
                @param {HttpRequest} request - The request object.
            The request body can contain:
                - id (objectId str) [REQUIRED]
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
                - status (str)
        @return: A Response object with the updated task data or an error message.

        @example javascript
            await fetch(`/api/v1/tasks/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({id: '1234', name: 'Task2'},
            });

        """
        responseData, httpStatus = self.updateTask(
            request.data, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def delete(self, request):
        """
        Deletes a task or list of task. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The query parameters MUST be:
                - id (objectID str) [REQUIRED]

        @return: A Response object with a success or an error message.

        @example javascript:

            fetch(`/api/v1/tasks?id=12345`, {
                method: 'DELETE',
            });
        """

        responseData, httpStatus = self.deleteTasks(
            request.query_params, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    @staticmethod
    def getTasks(taskData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to get tasks
        Gets tasks based on  input parameters.

        @param taskData      Dict for a single task or list of dicts for multiple tasks.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        userID = decodeApiKey(authorizationToken).get("userID")

        # Only get tasks for projects that contain the user
        projectIDs = [
            str(project.id) for project in Project.objects.filter(userIDs=userID)
        ]
        tasks = Task.objects.filter(**taskData, projectID__in=projectIDs)

        if not tasks:
            return {
                "message": "No tasks were found or you do not have authorization."
            }, status.HTTP_400_BAD_REQUEST

        serializer = TaskSerializer(tasks, many=True)

        return serializer.data, status.HTTP_200_OK

    @staticmethod
    def createTasks(taskData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to create tasks
        Creates a single task or multiple tasks based on the input data.


        @param taskData      Dict for a single task or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """

        # Normalize taskData to a list if it's a single task
        if not isinstance(taskData, list):
            taskData = [taskData]

        userID = decodeApiKey(authorizationToken).get("userID")
        projectIDs = set()

        for task in taskData:
            # Not required in serializer (would mess up gets) so need to check ourselves
            if "projectID" not in task:
                return (
                    {"message": "Parameter 'projectID' required"},
                    status.HTTP_400_BAD_REQUEST,
                )
            projectIDs.add(task["projectID"])

        # Only allow tasks for projects that contains the user
        authorizedProjectCount = Project.objects.filter(
            id__in=projectIDs, userIDs=userID
        ).count()
        if authorizedProjectCount != len(projectIDs):
            return {
                "message": "User not authorized to create task(s) for at least one project"
            }, status.HTTP_403_FORBIDDEN

        serializer = TaskSerializer(data=taskData, many=True)
        if serializer.is_valid():
            serializer.save()  # Save the task(s) to the database
            return serializer.data, status.HTTP_201_CREATED
        return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def updateTask(taskData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to update task.

        @param taskData      Dict for a single task.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        if "id" not in taskData:
            return "Error: Parameter 'id' required", status.HTTP_400_BAD_REQUEST

        try:
            task = Task.objects.get(id=taskData["id"])
        except Task.DoesNotExist:
            return None, status.HTTP_404_NOT_FOUND

        # Check if userID is in the project the task belongs to
        userID = decodeApiKey(authorizationToken).get("userID")
        project = Project.objects.get(id=task["projectID"])
        if ObjectId(userID) not in project["userIDs"]:
            return {
                "message": "User not authorized to edit this task"
            }, status.HTTP_403_FORBIDDEN

        serializer = TaskSerializer(data=taskData, instance=task, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates tasks
            return serializer.data, status.HTTP_200_OK

        return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def deleteTasks(taskData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to delete tasks.

        @param taskData      Dict for a single task.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """

        # Check
        if "id" not in taskData and "projectID" not in taskData:
            return (
                {"message", "Error: Parameter 'id' or 'projectID' required"},
                status.HTTP_400_BAD_REQUEST,
            )

        userID = decodeApiKey(authorizationToken).get("userID")
        if "id" in taskData:
            task = Task.objects.get(id=taskData["id"])
            # Check if userID is in the project the task belongs to
            project = Project.objects.get(id=task["projectID"])
            if ObjectId(userID) not in project["userIDs"]:
                return {
                    "message": "User not authorized to delete this task"
                }, status.HTTP_403_FORBIDDEN

            childTasks = Task.objects(parentTaskID=task["id"])
            for childTask in childTasks:
                message, httpsCode = TasksAPIView.updateTask(
                    {"id": childTask["id"], "parentTaskID": task["parentTaskID"]},
                    authorizationToken,
                )
                if httpsCode != status.HTTP_200_OK:
                    print(
                        f"Error moving children while deleting task: {message.get('message')}"
                    )
                    return (
                        f"Error moving children while deleting task: {message.get('message')}",
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            numberObjectsDeleted = Task.objects(id=taskData["id"]).delete()
        else:  # projectIDs
            # Check if userID is in the project
            project = Project.objects.get(id=taskData["projectID"])
            if ObjectId(userID) not in project["userIDs"]:
                return {
                    "message": "User not authorized to delete these task(s)"
                }, status.HTTP_403_FORBIDDEN

            numberObjectsDeleted = Task.objects(
                projectID=taskData["projectID"]
            ).delete()

        if numberObjectsDeleted == 0:
            return "No tasks found to delete.", status.HTTP_404_NOT_FOUND

        return "Task(s) Deleted Successfully", status.HTTP_200_OK
