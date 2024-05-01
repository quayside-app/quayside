from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.models import Task
from api.serializers import TaskSerializer
from api.decorators import apiKeyRequired
from api.views.v1.tasks import TasksAPIView
from api.views.v1.projects import ProjectsAPIView
from api.utils import getAuthorizationToken


@method_decorator(apiKeyRequired, name="dispatch")
class KanbanAPIView(APIView):
    """"
    Get and update a kanban board.
    Includes an endpoint to get a kanban and an endpoint to update a kanban.
    Also includes three static functions.
    Two to get and update a kanban and one to correctly format the priority field of the Task object.
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

        @param {HttpRequest} request - The request object.
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
            return "Error: paramter 'projectID' required.", status.HTTP_400_BAD_REQUEST
        
        try:
            tasks = Task.objects.filter(projectID=taskData.get("projectID"))
        except Task.DoesNotExist:
            return "Tasks not found for the specified projectID.", status.HTTP_404_NOT_FOUND
        
        data, httpsCode = ProjectsAPIView.getProjects({"id": tasks[0]["projectID"]})
        taskStatues = data.taskStatues

        if httpsCode != status.HTTP_200_OK:
            print(f"Project GET failed: {data.get('message')}")
            return data, httpsCode
        
        tasks_by_status = {}
        tasks_by_status["statues"] = sorted(taskStatues.items(), key=lambda status: status.get("order"))

        tasks_by_status["taskLists"] = []

        # creates empty task lists for each kanban type
        for stat in tasks_by_status["statues"]:
            tasks_by_status["taskLists"][stat.append([])]

        for i, task in reversed(list(enumerate(tasks))):
            # if task does not have a statusId it's put in the first set of tasks or the
            # left most size of the kanban board
            if not task.statusId or tasks_by_status["statues"][i].id == task.statusId:
                tasks_by_status["taskLists"].append(tasks.pop(i))

        # if a status associated with a task no longer exists, put it on the left most column as well
        for tasks in reversed(list(enumerate(tasks))):
            tasks_by_status["taskLists"].append(tasks.pop(i))

        for taskList in tasks_by_status["taskLists"]:
            KanbanAPIView.normalizePriority(taskList)
            TaskSerializer(tasks_by_status["taskLists"], many=True).data

        if tasks_by_status["taskLists"]:
            return tasks_by_status, status.HTTP_200_OK
        else:
            return "No tasks found for the specified projectID.", status.HTTP_404_NOT_FOUND
        
    @staticmethod
    def updateKanban(taskData):
        """
        Service API function that can be called internally as well as through the API to get a kanban.
        Updates kanban based on task id, status, and priority.

        @param:
            taskData (dict): Dict of parameters. Contains id, status, and priority.
                id (string): Id of the task to update.
                status (string): The status to update task to.
                priority (int): The priority to update task to.
                
        @return:
            A tuple of (response_data, http_status).
        """
        if 'id' not in taskData:
            return "Error: paramter 'id' required.", status.HTTP_400_BAD_REQUEST
        
        if 'priority' not in taskData:
            return "Error: parameter 'priority' required.", status.HTTP_400_BAD_REQUEST
        
        if 'status' not in taskData:
            return "Error: parameter 'status' required.", status.HTTP_400_BAD_REQUEST
        

        task_id = taskData.get('id')
        try:
            updating_task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return "Task not found with the provided ID.", status.HTTP_404_NOT_FOUND


        project = updating_task.projectID
        old_statusId = updating_task.statusId
        old_priority = updating_task.priority
        new_status_id = taskData.get('statusId')
        new_priority = taskData.get('priority')


        old_status_tasks = Task.objects.filter(
            projectID=project, 
            status=old_statusId, 
            priority__gt=old_priority
        ) # .update(priority = F['priority'] - 1)

        new_status_tasks = Task.objects.filter(
            projectID=project,
            status=new_status_id,
            priority__gte=new_priority
        ) # .update(priority = F['priority'] + 1)

        # TODO: find a better way to save a list of objects at once.
        # Everything I tried didn't work with mongoengine.
        for task in old_status_tasks:
            task.priority -= 1
            task.save()

        for task in new_status_tasks:
            task.priority += 1
            task.save()


        updating_task.statusId = new_status_id 
        updating_task.priority = new_priority
        updating_task.save()

        return "Kanban successfully updated.", status.HTTP_200_OK
        
    @staticmethod
    def normalizePriority(taskList):
        """
        Normalize the priority of tasks within each status group.
        Ensures all tasks have an integer priority value.
        Also ensures priority starts at 0 and is spaced evenly by 1.

        Source for sorting list, pushing none values to end:
        https://stackoverflow.com/questions/18411560/sort-list-while-pushing-none-values-to-the-end

        Args:
            tasks_by_status (dict): Dictionary containing tasks grouped by status.

        Returns:
            dict: Updated tasks grouped by status with normalized priorities.
        """

        taskList = sorted(taskList, key = lambda x: x["priority"])
        
        # Space priority evenly.
        for index, task in enumerate(taskList):
            if task['priority'] != index:
                task['priority'] = index
                task.save()
