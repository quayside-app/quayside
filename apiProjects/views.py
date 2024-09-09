from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from api.decorators import apiKeyRequired
from .serializers import ProjectSerializer, StatusSerializer
from .models import Project, Status
from apiTasks.views import TasksAPIView
from apiTasks.models import Task  # TODO: Remove references to this and replace with TaskAPI Functions???
from apiTasks.serializers import TaskSerializer
from api.utils import getAuthorizationToken, decodeApiKey



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
                - profileIDs (list[ObjectId])
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
            fetch('quayside.app/api/v1/projects?profileIDs=1234');
        """
        responseData, httpStatus = self.getProjects(
            request.query_params.dict(), getAuthorizationToken(request)
        )
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
                - profileIDs (list[ObjectId])
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
                - types (list[str])
                - objectives (list[str])
                - startDate (date, 'YYYY-MM-DD')
                - endDate (date, 'YYYY-MM-DD')
                - budget (str)
                - assumptions (list[str])
                - scopesIncluded (list[str])
                - scopesExcluded (list[str])
                - risks (list[str])
                - profileIDs (list[ObjectId])
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
        responseData, httpStatus = self.updateProject(
            request.data, getAuthorizationToken(request)
        )
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

        responseData, httpStatus = self.deleteProjects(
            request.query_params, getAuthorizationToken(request)
        )
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
            profileID = decodeApiKey(authorizationToken).get("profileID")

            if "profileIDs" not in projectData:
                projectData["profileIDs"] = []
            elif not isinstance(projectData["profileIDs"], list):
                projectData["profileIDs"] = [projectData["profileIDs"]]
            if profileID not in projectData["profileIDs"]:
                projectData["profileIDs"].append(profileID)

            projects = Project.objects.filter(
                profileIDs__in=projectData.pop("profileIDs"), **projectData
            )  

            if not projects:
                return {
                    "message": "No projects were found or you do not have authorization."
                }, status.HTTP_400_BAD_REQUEST
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
        if "_id" in projectData:
            projectData["id"] = projectData.pop("_id")
        if "id" not in projectData:
            return "Error: Parameter 'id' required", status.HTTP_400_BAD_REQUEST

        try:
            project = Project.objects.get(id=projectData["id"])
        except ObjectDoesNotExist:
            return "Project not found", status.HTTP_404_NOT_FOUND

        # Check if profileID is in the project's list of UserIDs
        profileID = decodeApiKey(authorizationToken).get("profileID")
        if not project.profileIDs.filter(id=profileID).exists():
            return {
                "message": "User not authorized to edit this project"
            }, status.HTTP_403_FORBIDDEN

        serializer = ProjectSerializer(data=projectData, instance=project, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates projects
            return serializer.data, status.HTTP_200_OK

        print(serializer.errors)
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
        profileID = decodeApiKey(authorizationToken).get("profileID")

        if "profileIDs" not in projectData or projectData["profileIDs"] != [profileID]:
            return {
                "message": "Request data must contain a list of profileIDs with only your user ID present."
            }, status.HTTP_400_BAD_REQUEST

        if isinstance(projectData, list):
            serializer = ProjectSerializer(data=projectData, many=True)
        else:
            serializer = ProjectSerializer(data=projectData)

        if serializer.is_valid():
            serializer.save()  # Save the project(s) to the database

            # Create statuses
            defaultStatuses = [
                {
                    "name": "Todo",
                    "color": "323232", # html color code
                    "order": 1 # task order on kanban
                },
                {
                    "name": "In-Progress",
                    "color": "EFA610",
                    "order": 2 # task order on kanban
                },
                {
                    "name": "Done",
                    "color": "01796E", # html color code
                    "order": 3 # task order on kanban
                }
            ]

            for defaultStatus in defaultStatuses:
                defaultStatus['project'] = serializer.data["id"]
                data, statusCode = StatusesAPIView.createStatus(defaultStatus, authorizationToken)
                if statusCode != status.HTTP_201_CREATED:
                    return {"message": f"There was an error creating default statuses for the project: {data}"}, statusCode
            # Returns data including new primary key
            return serializer.data, status.HTTP_201_CREATED
        return {"message":serializer.errors}, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def deleteProjects(projectData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to delete
        project and all associated tasks.

        @param projectData      Dict for a single project
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        if "id" not in projectData:
            return {"message": "Parameter 'id' required"}, status.HTTP_400_BAD_REQUEST
        ID = projectData["id"]
        project = Project.objects.get(id=ID)

        profileID = decodeApiKey(authorizationToken).get("profileID")

        if not project.profileIDs.filter(id=profileID).exists():
            return {
                "message": "Not authorized to delete project."
            }, status.HTTP_401_UNAUTHORIZED

        message, httpsCode = TasksAPIView.deleteTasks(
            {"projectID": ID}, authorizationToken
        )
        if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
            return message, httpsCode

        numberObjectsDeleted = project.delete()
        if numberObjectsDeleted == 0:
            return "No project found to delete.", status.HTTP_404_NOT_FOUND

        return "Project Deleted Successfully", status.HTTP_200_OK




@method_decorator(apiKeyRequired, name="dispatch")  # dispatch protects all HTTP requests coming in
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
        Creates status(es). Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body can contain:
                - id (objectID str)
                - name (str)
                - color (str)
                - order (str)
        @param {str} authorizationToken - JWT authorization token.

        @return A response telling you if the status was created.

        @example javascript:

            fetch('quayside.app/api/v1/statuses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "projectID": "5AC9942376", "name":  "backlog", "color": "A4279", "order":  2 }),
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
                body: JSON.stringify({ "projectID": "5AC9942376", "name":  "backlog", "color": "A4279", "order":  2 }),
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
    def getStatuses(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to get
        status data based on input data.

        @param statusData      Dict for getting status 
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """

        try:
            # Only get project where user is a contributor
            profileID = decodeApiKey(authorizationToken).get("profileID") 
            statuses = Status.objects.filter(**statusData, project__profileIDs=profileID)
            serializer = StatusSerializer(statuses, many=True)
            return serializer.data, status.HTTP_200_OK
        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def updateStatus(statusData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to update
        project data based on input data.

        @param statusData      Dict for a single status.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """

        
        if "id" not in statusData:
            return "Error: Parameter 'id' required", status.HTTP_400_BAD_REQUEST

        try:
            status = Status.objects.get(id=statusData["id"])
        except ObjectDoesNotExist:
            return "Status not found", status.HTTP_404_NOT_FOUND

        # Check if profileID is in the project's list of UserIDs
        profileID = decodeApiKey(authorizationToken).get("profileID")
        if not Status.objects.filter(id=statusData["id"], project__profileIDs__id=profileID).exists():
                return {
                    "message": "No statuses were found or you do not have authorization."
                }, status.HTTP_400_BAD_REQUEST
        serializer = StatusSerializer(data=statusData, instance=status, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates projects
            return serializer.data, status.HTTP_200_OK

        print(serializer.errors)
        return serializer.errors, status.HTTP_400_BAD_REQUEST

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

            # Check if profile can access project
            profileID = decodeApiKey(authorizationToken).get("profileID")
            if not Project.objects.filter(id=statusData["project"], profileIDs__id=profileID).exists():
                return {
                    "message": "No projects were found or you do not have authorization."
                }, status.HTTP_400_BAD_REQUEST

            serializer = StatusSerializer(data=statusData)

            if serializer.is_valid():
                serializer.save()  # Updates projects
                return {"message":"Successfully created status"}, status.HTTP_201_CREATED
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
            data=data[0]

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
        Retrieves and array of tasks for the number of statuses associated with the project
        that are ordered by status.order and an array of status objects that are also ordered
        using the `order` property.

        Requires 'apiToken' passed in auth header or cookies

        @param {HttpRequest} request - The request object.
            Query Parameters:
                - projectID (objectId str)


        @return: A Response object containing projects tasks grouped by status.

        @response example:
            {
                "statuses": [
                    {
                        "id": 123, "name": "Backlog", "order": 1, "color": "A13D23"
                        "id": 423, "name": "Todo", "order": 2, "color": "A13D42"
                        "id": 444, "name": "Done", "order": 3, "color": "A13D99"
                    },
                ],
                "taskLists": [
                    # tasks that have a statusId of 123, no statusId, a statusId of None, or statusId not in `statuses`
                    [taskObject, taskObject, taskObject, taskObject],
                    # tasks that have a statusId of 423
                    [taskObject, taskObject, taskObject, taskObject],
                    # tasks that have a statusId of 444
                    [taskObject, taskObject, taskObject, taskObject]
                ]
            }
        
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
                - name (str)
                - order (int)
                - color (str)

        @return: A response object with the changes made or an error message
        
        @example Javascript:

            fetch('quayside.app/api/v1/kanban', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({id: '1234', status: 'Todo', order: 4})
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
        
        print(tasks)
        print("HEREREREERER--------------1")
        
        try:
            data, httpsCode = StatusesAPIView.getStatuses({"project": tasks[0].projectID}, authorizationToken)

            if httpsCode != status.HTTP_200_OK:
                print(f"Project GET failed: {data.get('message')}")
                return data, httpsCode
            
            tasks_by_status = {}
            print("HEREREREREREREERERE-------------------2")
            # Sort each status by the 'order' number which is used to define the order of kanban columns from left to right
            tasks_by_status["statuses"] = sorted(data, key=lambda status: status.get("order"))
            print("HEREREREREREREERERE-------------------2.1")
            
            # include a status with an id of None to the front of the status array to account for the case where
            # a task does not have a status id associated with it or it is set to the default value None
            tasks_by_status["statuses"].insert(0, {'id': None})

            # Create a dictionary that maps each statusId from the sorted status dictionaries with an index
            status_id_order_dict = { stat['id'] if stat['id'] != None else None: index for index, stat in enumerate(tasks_by_status["statuses"]) }

            # removing None from status ids since it's only added for creating a statusId mapping
            del tasks_by_status["statuses"][0]

            # Creates a sorted list of tasks using the custom statusId mapping. If a statusId associated with
            # a task doesn't existing in the mapping, is None, or non-existent it's at the start of the list
            # and it will appear on the leftmost column
            print("HEREREREREREREERERE-------------------2.2")
            sorted_tasks = sorted(tasks, key=lambda task: status_id_order_dict[None if 'status' not in task or task.status not in status_id_order_dict.keys() else task['status']])

            tasks_by_status["taskLists"] = []
            
            print("HEREREREREREREERERE-------------------3")
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
                KanbanAPIView.normalizeTaskPriorityAndStatus(taskList, tasks_by_status["statuses"][i]["id"])
                serialized_data = TaskSerializer(taskList, many=True)
                
                tasks_by_status["taskLists"][i] = serialized_data.data

            print("HEREREREREREREERERE-------------------4")

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
