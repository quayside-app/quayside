from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Task
from api.serializers import TaskSerializer
from rest_framework import status


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
        
    
    def post(self, request):
        """
        Updates  task(s)

        TODO comment
        TODO TEST
        """
        response_data, http_status = self.updateTasks(request.data)
        return Response(response_data, status=http_status)

    def delete(self, request):
        """
        Deletes a task or list of tasks

        TODO MORE COMMENTS
        TODO TEST

        @return: A Response object with the created task(s) data or an error message.
        """

        responseData, httpStatus = self.createTasks(request.query_params)
        return Response(responseData, status=httpStatus)

    @staticmethod
    def createTasks(taskData):
        """
        Service API function that can be called internally as well as through the API to create tasks
        Creates a single task or multiple tasks based on the input data.

        @param task_data      Dict for a single task or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """
        if isinstance(taskData, list):
            serializer = TaskSerializer(data=taskData, many=True)
        else:
            serializer = TaskSerializer(data=taskData)
        
        if serializer.is_valid():
            serializer.save()  # Save the task(s) to the database
            return serializer.data, status.HTTP_201_CREATED
        else:
            return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def updateTasks(taskData):
        """
        TODO commentss
        """
        if isinstance(taskData, list):
            serializer = TaskSerializer(data=taskData, many=True)
        else:
            serializer = TaskSerializer(data=taskData)
        
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
