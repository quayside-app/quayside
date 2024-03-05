from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Task
from api.serializers import TaskSerializer
from rest_framework import status

from django.utils.decorators import method_decorator
from api.decorators import apiKeyRequired

@method_decorator(apiKeyRequired, name='dispatch')  # dispatch protects all HTTP requests coming in
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
        responseData, httpStatus = self.getTasks(request.query_params.dict())
        return Response(responseData, status=httpStatus)

    def post(self, request):
        """
        Creates a single task or a list of tasks. MUST have projectID.

        Expected JSON Body Format:
            Single Task:
                {
                    "projectID": "objectId str",
                    "name": "str",
                    ...
                }

            List of Tasks:
                [
                    {
                        "projectID": "objectId str",
                        "name": "str",
                        ...
                    },
                    ...
                ]

        @return: A Response object with the created task(s) data or an error message.
        """
        responseData, httpStatus = self.createTasks(request.data)
        return Response(responseData, status=httpStatus)

    def put(self, request):
        """
        Updates single task

        TODO comment
        TODO TEST
        """
        responseData, httpStatus = self.updateTask(request.data)
        return Response(responseData, status=httpStatus)

    def delete(self, request):
        """
        Deletes a task or list of tasks

        TODO MORE COMMENTS
        TODO TEST

        @return: A Response object with the created task(s) data or an error message.
        """

        responseData, httpStatus = self.deleteTasks(request.query_params)
        return Response(responseData, status=httpStatus)

    @staticmethod
    def getTasks(taskData):
        """
        Service API function that can be called internally as well as through the API to get tasks
        Gets tasks based on  input parameters.
        TODO COMMENTS

        @param taskData      Dict for a single task or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """

        #! TODO: Filter query params to prevent injection attack?!!

        projects = Task.objects.filter(**taskData)  # Query mongo

        serializer = TaskSerializer(projects, many=True)

        return serializer.data, status.HTTP_200_OK

    @staticmethod
    def createTasks(taskData):
        """
        Service API function that can be called internally as well as through the API to create tasks
        Creates a single task or multiple tasks based on the input data.

        TODO COMMENTS

        @param taskData      Dict for a single task or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """

        if isinstance(taskData, list):
            serializer = TaskSerializer(data=taskData, many=True)
            for task in taskData:
                # Not required in serializer (would mess up gets) so need to check ourselves
                if "projectID" not in task:
                    return "Error: Parameter 'projectID' required", status.HTTP_400_BAD_REQUEST
        else:
            serializer = TaskSerializer(data=taskData)
            if "projectID" not in taskData:
                return "Error: Parameter 'projectID' required", status.HTTP_400_BAD_REQUEST

        if serializer.is_valid():
            serializer.save()  # Save the task(s) to the database
            return serializer.data, status.HTTP_201_CREATED
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def updateTask(taskData):
        """
        TODO commentss
        """
        if "id" not in taskData:
            return "Error: Parameter 'id' required", status.HTTP_400_BAD_REQUEST

        try:
            task = Task.objects.get(id=taskData["id"])
        except Task.DoesNotExist:
            return None, status.HTTP_404_NOT_FOUND 

       
        serializer = TaskSerializer(data=taskData, instance=task, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates tasks
            return serializer.data, status.HTTP_200_OK
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def deleteTasks(taskData):
        """
        TODO comments
        """

        # TODO try/accept??

        # Check
        if "id" not in taskData and "projectID" not in taskData:
            return "Error: Parameter 'id' or 'projectID' required", status.HTTP_400_BAD_REQUEST

        if "id" in taskData:
            numberObjectsDeleted = Task.objects(id=taskData["id"]).delete()
        else:  # projectIDs
            numberObjectsDeleted = Task.objects(
                projectID=taskData["projectID"]).delete()

        if numberObjectsDeleted == 0:
            return "No tasks found to delete.", status.HTTP_404_NOT_FOUND

        return "Task(s) Deleted Successfully", status.HTTP_200_OK
