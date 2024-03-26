from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.models import Task
from api.serializers import TaskSerializer
from api.decorators import apiKeyRequired


@method_decorator(apiKeyRequired, name="dispatch")
class KanbanAPIView(APIView):
    """"
    Get a kanban board.
    """

    def get(self, request):
        """
        Retrieves tasks of the specified project grouped by status.

        @param {HttpRequest} request - The request object.
            Query Parameters:
                - projectID (objectId str)


        @return: A Response object containing projects tasks grouped by status.
        
        @example Javascript:
            fetch('quayside.app/api/v1/kanban?projectID=1234');
        """
        responseData, httpStatus = self.getKanban(request.query_params)
        return Response(responseData, status=httpStatus)
    
    @staticmethod
    def getKanban(taskData):
        """
        Service API function that can be called internally as well as through the API to get a kanban.
        Gets kanban based on projectID within taskData.

        @param taskData     Dict of parameters. Only projectID considered.
        @return      A tuple of (response_data, http_status).
        """
        if "projectID" not in taskData:
            return "Error: paramter 'projectID' required", status.HTTP_400_BAD_REQUEST
        
        try:
            tasks = Task.objects.filter(projectID=taskData.get("projectID"))
        except Task.DoesNotExist:
            return "Tasks not found for the specified projectID", status.HTTP_404_NOT_FOUND


        tasks_by_status = {}
        for task in tasks:
            kanbanStatus = task.kanbanStatus
            if kanbanStatus not in tasks_by_status:
                tasks_by_status[kanbanStatus] = []
            tasks_by_status[kanbanStatus].append(task)

        serialized_data = {}
        for kanban_status, task_list in tasks_by_status.items():
            serialized_tasks = TaskSerializer(task_list, many=True).data
            serialized_data[kanban_status] = serialized_tasks

        if serialized_data:
            return serialized_data, status.HTTP_200_OK
        else:
            return "No tasks found for the specified projectID", status.HTTP_404_NOT_FOUND