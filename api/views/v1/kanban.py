from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.models import Task
from api.serializers import TaskSerializer
from api.decorators import apiKeyRequired
from api.views.v1.tasks import TasksAPIView


@method_decorator(apiKeyRequired, name="dispatch")
class KanbanAPIView(APIView):
    """"
    Get and update a kanban board.
    """

    def get(self, request):
        """
        Retrieves tasks of the specified project grouped by status.
        Requires 'apiToken' passed in auth header or cookies

        @param {HttpRequest} request - The request object.
            Query Parameters:
                - projectID (objectId str)


        @return: A Response object containing projects tasks grouped by status.
        
        @example Javascript:
            fetch('quayside.app/api/v1/kanban?projectID=1234');
        """
        responseData, httpStatus = self.getKanban(request.query_params)
        return Response(responseData, status=httpStatus)
    
    def put(self, request):
        """
        Updates a kanban board.
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} requaest - The request object.
            The request body can contain:
                - id (objectId str) [REQUIRED]
                - status (str)
                - priority (int) [REQUIRED]

        @return: A response object with the changes made or an error message
        
        @example Javascript:

            fetch('quayside.app/api/v1/kanban', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({id: '1234', status: 'Todo', priority: 4})
            })

        """
        responseData, httpStatus = self.updateKanban(request.data)
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
            kanbanStatus = task.status
            if kanbanStatus not in tasks_by_status:
                tasks_by_status[kanbanStatus] = []
            tasks_by_status[kanbanStatus].append(task)

        tasks_by_status = KanbanAPIView.normalizePriority(tasks_by_status)


        serialized_data = {}
        for kanban_status, task_list in tasks_by_status.items():
            serialized_tasks = TaskSerializer(task_list, many=True).data
            serialized_data[kanban_status] = serialized_tasks

        if serialized_data:
            return serialized_data, status.HTTP_200_OK
        else:
            return "No tasks found for the specified projectID", status.HTTP_404_NOT_FOUND
        
    @staticmethod
    def updateKanban(taskData):
        """
        Service API function that can be called internally as well as through the API to get a kanban.
        Updates kanban based on id, status, and priority.

        @param taskData     Dict of parameters. Only id, status, and priority are considered.
        @return      A tuple of (response_data, http_status).
        """
        ###PSUEDO CODE###
        # Take task out of status list.
        # All tasks with a priority number greater in status list -= 1 priority.
        # Then task is inserted into its new status (which could be the same one) and is given its new priority.
        # All tasks with a greater piority in that status += 1 priority.
        if 'id' not in taskData:
            return "Error: paramter 'id' required", status.HTTP_400_BAD_REQUEST
        
        if 'priority' not in taskData:
            return "Error: parameter 'priority' required", status.HTTP_400_BAD_REQUEST
        
        task_id = taskData.get('id')
        new_status = taskData.get('status')
        new_priority = taskData.get('priority')

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return "Task not found with the provided ID", status.HTTP_404_NOT_FOUND
        
        if new_status:
            task.status = new_status
 
        other_tasks = Task.objects.filter(projectID=task.projectID, status=task.status).order_by('priority')

        print(other_tasks)

        return "update kanban was called", status.HTTP_200_OK
        
    @staticmethod
    def normalizePriority(tasks_by_status):
        """
        Normalize the priority of tasks within each status group.
        Ensures all tasks have an integer priority value.
        Also ensures priority starts at 0 and is spaced evenly by 1.

        Args:
            tasks_by_status (dict): Dictionary containing tasks grouped by status.

        Returns:
            dict: Updated tasks grouped by status with normalized priorities.
        """
        # Loop through status.
        for status_name, task_list in tasks_by_status.items():
            # Initialize null priority.
            for index, task in enumerate(task_list):
                if task.priority is None:
                    task.priority = index
                    task.save()

            sorted_tasks = sorted(task_list, key=lambda x: x.priority)

            # Space priority evenly.
            for index, task in enumerate(sorted_tasks):
                if task.priority != index:
                    task.priority = index
                    task.save()

        return tasks_by_status
