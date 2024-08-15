import os
import re
from dotenv import load_dotenv
import openai

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from django.utils.decorators import method_decorator

from .models import Task, Project
from .serializers import TaskSerializer, GeneratedTaskSerializer
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
                - durationMinutes (int)


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
                - durationMinutes (int)

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
                - durationMinutes (int)
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
            The query parameters can be (either id or projectID is required):
                - id (objectID str)  If passed, deletes that project.
                - projectID (objectID str) If passed, deletes all tasks in a project.
                - deleteChildren (bool str) "true" deletes current task and all children , "false" just 
                    deletes current node (if id passed).



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
        profileID = decodeApiKey(authorizationToken).get("profileID")
        
        # Only get tasks for projects that contain the user
        projectIDs = [
            str(project.id) for project in Project.objects.filter(profileIDs=profileID)
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

        profileID = decodeApiKey(authorizationToken).get("profileID")
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
            id__in=projectIDs, profileIDs=profileID
        ).count()
        if authorizedProjectCount != len(projectIDs):
            return {
                "message": "User not authorized to create task(s) for at least one project"
            }, status.HTTP_403_FORBIDDEN

        serializer = TaskSerializer(data=taskData, many=True)
        if serializer.is_valid():
            serializer.save()  # Save the task(s) to the database
            return serializer.data, status.HTTP_201_CREATED
        return {'message' : serializer.errors}, status.HTTP_400_BAD_REQUEST

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

        # Check if profileID is in the project the task belongs to
        profileID = decodeApiKey(authorizationToken).get("profileID")
        project = Project.objects.get(id=task["projectID"])
        if ObjectId(profileID) not in project["profileIDs"]:
            return {
                "message": "User not authorized to edit this task"
            }, status.HTTP_403_FORBIDDEN

        serializer = TaskSerializer(data=taskData, instance=task, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates tasks
            return serializer.data, status.HTTP_200_OK

        return {"message":serializer.errors}, status.HTTP_400_BAD_REQUEST

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

        profileID = decodeApiKey(authorizationToken).get("profileID")
        numberObjectsDeleted = 0
        if "id" in taskData:
            task = Task.objects.get(id=taskData["id"])
            # Check if profileID is in the project the task belongs to
            print("HERE1")
            project = task.projectID
            print("HERE2")
            print("HERE2.01")
            if not project.profileIDs.filter(id=profileID).exists():  # profileID not in project.profileIDs 
                return {
                    "message": "User not authorized to delete this task"
                }, status.HTTP_403_FORBIDDEN
            print("HERE 2.02")
            if taskData.get("deleteChildren", "false") == "true":
                print("HERE2.1")
                numberObjectsDeleted = deleteAllChildren(taskData["id"])
            else:
                print("HERE2.5")
                childTasks = task.childTasks.all() # Task.objects(parentTaskID=task)
                for childTask in childTasks:
                    message, httpsCode = TasksAPIView.updateTask(
                        {"id": childTask["id"], "parentTaskID": task["parentTaskID"]},
                        authorizationToken,
                    )
                    print("HERE3")
                    if httpsCode != status.HTTP_200_OK:
                        print(
                            f"Error moving children while deleting task: {message.get('message')}"
                        )
                        return (
                            f"Error moving children while deleting task: {message.get('message')}",
                            status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )

                numberObjectsDeleted, _ = Task.objects.filter(id=taskData["id"]).delete()
        else:  # projectIDs
            # Check if profileID is in the project
            project = Project.objects.get(id=taskData["projectID"])
            if ObjectId(profileID) not in project["profileIDs"]:
                return {
                    "message": "User not authorized to delete these task(s)"
                }, status.HTTP_403_FORBIDDEN

            numberObjectsDeleted = Task.objects(
                projectID=taskData["projectID"]
            ).delete()

        if numberObjectsDeleted == 0:
            return {"message": "No tasks found to delete."}, status.HTTP_404_NOT_FOUND

        return {"message":"Task(s) Deleted Successfully"}, status.HTTP_200_OK

@staticmethod
def deleteAllChildren(taskID):
    """
    Recursively deletes a task and all its children, and returns the total count of deleted objects.
    @param taskID: ID of task to delete along with all its children.
    @return: Total number of tasks deleted.
    """
    numberObjectsDeleted = 0
    children = Task.objects(parentTaskID=taskID)
    for child in children:
        numberObjectsDeleted += deleteAllChildren(child.id)
    numberObjectsDeleted += Task.objects(id=taskID).delete()
    return numberObjectsDeleted







# Dispatch protects all HTTP requests coming in
@method_decorator(apiKeyRequired, name="dispatch")
class GeneratedTasksAPIView(APIView):
    """
    Generates and saves tasks with ChatGPT. Requires apiKey.
    """

    def post(self, request):
        """
        Generate and saves tasks for a project.
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body should include:
            - name: A string with the name/description of the project.
            - projectID: A string of the project ID.

        @returns {Response} - A Response object containing a JSON array of serialized Task objects.


        @example Javascript:

            fetch('quayside.app/api/v1/GeneratedTasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'New Project', projectID: '12345' }),
            });
        """
        responseData, httpStatus = self.generateTasks(
            request.data, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    @staticmethod
    def generateTasks(projectData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to generate
        and save tasks.
        @param {dict} projectData -  Requires 'name' and 'projectID' keys.
        @param authorizationToken      JWT authorization token.
        @returns {tuple} - A tuple containing the list of created tasks and the HTTP status code.
        """

        # Check
        serializer = GeneratedTaskSerializer(data=projectData)
        if not serializer.is_valid():
            return {"message":serializer.errors}, status.HTTP_400_BAD_REQUEST

        projectName = serializer.validated_data["name"]
        projectID = serializer.validated_data["projectID"]
        projectDescription = serializer.validated_data["description"]
        totalProjectMinutes = 0

        # Load ChatGPT creds
        load_dotenv()
        openai.api_key = os.getenv("CHATGPT_API_KEY")

        # Call ChatGPT
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are an assistant for quayside.app, a project management team. 
                    You are given as input a project or task that a single person or a team 
                    wants to take on. Divide the task into less than 5 subtasks and list them 
                    hierarchically in the format where task 1 has subtasks 1.1, 1.2,...
                    and task 2 has subtasks 2.1, 2.2, 2.3,... and so forth and allow for subtasks to 
                    have their own hierarcy in the format of 1.1.1, 1.1.2, 1.13,... and so forth. For each subtask without it's own hierarcy, 
                    provide a time estimation in minutes in square brackets with the label "minutes". Do not give a minute range.
                    Make sure that every task is on one line after the number and has a time estimation. 
                    NEVER create new paragraphs within a task or subtask.
                    """,
                },
                {"role": "user", "content": f"Project Name: {projectName}\nProject Description: {projectDescription}"},
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        generatedString = completion.choices[0].message.content


        # Parse response into tasks with durations
        newTasks = []
        lines = generatedString.split("\n")

        degreeOfSeparation = 1
        subtasks = []

        for line in reversed(lines):
            strDuration = re.search(r"\[(\d+(?:\.\d+)?)\s*(minute|hour|day|week)(?:s)?\]", line) # parses duration from text between brackets returned by OpenAI

            # minimum minutes
            durationMinutes = 0
            if strDuration:
                line = line[0 : line.rfind(" [")]

            primaryTaskMatch = re.match(r"^(\d+)\.\s(.+)", line)
            subTaskMatch = re.match(r"^\s+(\d+\.(\d+|\d+\.)+)?\s(.+)", line)
            
            if strDuration:
                type = strDuration.group(2)

                if type.find("week") != -1:
                    durationMinutes = int(5 * 8 * 60 * float(strDuration.group(1)))
                elif type.find("day") != -1:
                    durationMinutes = int(8 * 60 * float(strDuration.group(1)))
                elif type.find("hour") != -1:
                    durationMinutes = int(60 * float(strDuration.group(1)))
                else:
                    durationMinutes = int(strDuration.group(1))

            if primaryTaskMatch or subTaskMatch:
                allTaskNumbers = (subTaskMatch[1] if subTaskMatch else primaryTaskMatch[1]).split(".")

                if (allTaskNumbers[-1] == ""):
                    allTaskNumbers.pop(-1)

            if subTaskMatch:
                if degreeOfSeparation == 1:
                    degreeOfSeparation = len(allTaskNumbers)

                subTaskText = subTaskMatch[3]
                
                currentSubtask = {
                    "id": allTaskNumbers[-1],
                    "name": subTaskText,
                    "parent": allTaskNumbers[-2],
                    "durationMinutes": durationMinutes
                }

                if degreeOfSeparation > len(allTaskNumbers) or degreeOfSeparation == 1:
                    degreeOfSeparation = len(allTaskNumbers) # aka degreeOfSeparation -= 1

                    totalMinutes = 0
                    for task in subtasks:
                        totalMinutes += task["durationMinutes"]

                    currentSubtask["durationMinutes"] = totalMinutes
                    currentSubtask["subtasks"] = subtasks[:]
                    subtasks.clear()

                subtasks.insert(0, currentSubtask)
                    
            elif primaryTaskMatch:
                taskText = primaryTaskMatch[2]

                totalMinutes = 0
                for task in subtasks:
                    totalMinutes += task["durationMinutes"]
                    
                totalProjectMinutes += totalMinutes if totalMinutes > 0 else durationMinutes
                
                newTasks.insert(0, 
                    {
                        "id": allTaskNumbers[0],
                        "name": taskText,
                        "parent": "root",
                        "durationMinutes": totalMinutes if totalMinutes > 0 else durationMinutes,
                        "subtasks": subtasks[:],
                    }
                )

                subtasks.clear()

        # Save tasks

        # Function for Parsing Tasks. TODO: do this in 1 db write??
        def parseTask(task: dict, parentID: str, projectID: str):
            data, httpsCode = TasksAPIView.createTasks(
                {
                    "projectID": projectID,
                    "parentTaskID": parentID,
                    "name": task["name"],
                    "durationMinutes": task["durationMinutes"]
                },
                authorizationToken,
            )
            if httpsCode != status.HTTP_201_CREATED:
                return data, httpsCode
            taskData = data[0]
            if "subtasks" in task:
                for subtask in task["subtasks"]:
                    parseTask(subtask, taskData["id"], projectID)
            return taskData

        createdTasks = []

        # Create a root task if one does not exist
        rootID = None
        if len(newTasks) != 1:
            data, httpsCode = TasksAPIView.createTasks(

                {"projectID": projectID, "name": projectName, "durationMinutes": totalProjectMinutes}, authorizationToken

            )
            if httpsCode != status.HTTP_201_CREATED:
                return data, httpsCode
            taskData = data[0]

            rootID = taskData["id"]
            createdTasks.append(taskData)

        for task in newTasks:
            taskData = parseTask(task, rootID, projectID)
            createdTasks.append(taskData)

        return createdTasks, status.HTTP_201_CREATED
