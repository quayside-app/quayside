from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.models import Task
from api.serializers import TaskSerializer
from api.decorators import apiKeyRequired
from api.views.v1.tasks import TasksAPIView
from api.views.v1.statuses import StatusesAPIView
from api.utils import getAuthorizationToken
from bson.objectid import ObjectId


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
        responseData, httpStatus = self.getKanban(request.query_params, getAuthorizationToken(request))
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
    def getKanban(taskData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to get a kanban.
        Gets kanban based on projectID within taskData.

        @param taskData     Dict of parameters. Only projectID considered.
        @return      A tuple of (response_data, http_status).
        """
        if "projectID" not in taskData:
            return "Error: paramter 'projectID' required.", status.HTTP_400_BAD_REQUEST
        
        try:
            tasks = list(Task.objects.filter(projectID=taskData.get("projectID")))
        except Task.DoesNotExist:
            return "Tasks not found for the specified projectID.", status.HTTP_404_NOT_FOUND
        
        try:
            data, httpsCode = StatusesAPIView.getStatuses({"projectID": tasks[0]["projectID"]}, authorizationToken)

            if httpsCode != status.HTTP_200_OK:
                print(f"Project GET failed: {data.get('message')}")
                return data, httpsCode
            
            tasks_by_status = {}

            # Sort each status by the 'order' number which is used to define the order of kanban columns from left to right
            tasks_by_status["statuses"] = sorted(data, key=lambda status: status.get("order"))
            # include a status with an id of Noneto the front of the status array to account for the case where
            # a task does not have a status id associated with it or it is set to the default value None
            tasks_by_status["statuses"].insert(0, {'id': None})

            # Create a dictionary that maps each statusId from the sorted status dictionaries with an index
            status_id_order_dict = { ObjectId(stat['id']): index for index, stat in enumerate(tasks_by_status["statuses"]) }

            # removing None from status ids since it's only added for creating a statusId mapping
            del tasks_by_status["statuses"][0]

            # Creates a sorted list of tasks using the custom statusId mapping. If a statusId associated with
            # a task doesn't existing in the mapping, is None, or non-existent it's at the start of the list
            # and it will appear on the leftmost column
            sorted_tasks = sorted(tasks, key=lambda task: status_id_order_dict[None if 'statusId' not in task or task.statusId not in status_id_order_dict.keys() else task['statusId']])

            tasks_by_status["taskLists"] = []

            # creates an empty task lists for each status type
            for stat in data:
                tasks_by_status["taskLists"].append([])

            currentStatusId = list(status_id_order_dict.keys())[-1]
            statusIndex = len(tasks_by_status["taskLists"]) - 1

            # putting the sorted task objects into columns lists from right to left 
            for i, task in reversed(list(enumerate(sorted_tasks))):

                # while a task doesn't go into the current selected column
                while currentStatusId != task.statusId and statusIndex >= 1:
                    statusIndex -= 1
                    currentStatusId = list(status_id_order_dict.keys())[statusIndex+1]

                # instead of adding all remaining tasks indiviually into the leftmost column, dump them all at the same time
                if (statusIndex < 1):
                    tasks_by_status["taskLists"][statusIndex] = sorted_tasks
                    break
            
                tasks_by_status["taskLists"][statusIndex].append(sorted_tasks.pop(i))

            for i, taskList in enumerate(tasks_by_status["taskLists"]):
                KanbanAPIView.normalizeTaskPriorityAndStatus(taskList, ObjectId(tasks_by_status["statuses"][i]["id"]))
                serialized_data = TaskSerializer(taskList, many=True)
                
                tasks_by_status["taskLists"][i] = serialized_data.data

            if not tasks_by_status["taskLists"]:
                return "No tasks found for the specified projectID.", status.HTTP_404_NOT_FOUND

            return tasks_by_status, status.HTTP_200_OK
            
        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR

        
    @staticmethod
    def updateKanban(taskData):
        """
        Service API function that can be called internally as well as through the API to get a kanban.
        Updates kanban based on task id, status, and priority.

        @param:
            taskData (dict): Dict of parameters. Contains id, status, and priority.
                id (string): Id of the task to update.
                statusId (string): Reference to a status.
                priority (int): The priority to update task to.
                
        @return:
            A tuple of (response_data, http_status).
        """
        print(taskData)
        if 'id' not in taskData:
            return "Error: paramter 'id' required.", status.HTTP_400_BAD_REQUEST
        
        if 'priority' not in taskData:
            return "Error: parameter 'priority' required.", status.HTTP_400_BAD_REQUEST
        
        if 'statusId' not in taskData:
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
            statusId=old_statusId, 
            priority__gt=old_priority
        ) # .update(priority = F['priority'] - 1)

        new_status_tasks = Task.objects.filter(
            projectID=project,
            statusId=new_status_id,
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
    def normalizeTaskPriorityAndStatus(taskList, status_id):
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

        taskList = sorted(taskList, key = lambda x: x["priority"] if x.priority != None else 0)
        
        # Space priority evenly.
        for index, task in enumerate(taskList):
            if (task.priority != index) or ('statusId' not in task) or (task.statusId != status_id):
                task.priority = index
                task.statusId = status_id
                task.save()
