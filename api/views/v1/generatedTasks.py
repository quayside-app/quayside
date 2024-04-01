import os
from dotenv import load_dotenv
import re
import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.serializers import GeneratedTaskSerializer
from api.views.v1.tasks import TasksAPIView
from api.decorators import apiKeyRequired


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
        responseData, httpStatus = self.generateTasks(request.data)
        return Response(responseData, status=httpStatus)

    @staticmethod
    def generateTasks(projectData):
        """
        Service API function that can be called internally as well as through the API to generate
        and save tasks.
        @param {dict} projectData -  Requires 'name' and 'projectID' keys.
        @returns {tuple} - A tuple containing the list of created tasks and the HTTP status code.
        """

        # Check
        serializer = GeneratedTaskSerializer(data=projectData)
        if not serializer.is_valid():
            return serializer.errors, status.HTTP_400_BAD_REQUEST

        projectName = serializer.validated_data["name"]
        projectID = serializer.validated_data["projectID"]

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
                    and task 2 has subtasks 2.1, 2.2, 2.3,... and so forth. Make sure that every 
                    task is on one line after the number. NEVER create new paragraphs within a 
                    task or subtask.
                    """,
                },
                {"role": "user", "content": projectName},
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        generatedString = completion.choices[0].message.content

        # Parse response into tasks
        newTasks = []
        lines = generatedString.split("\n")

        currentTaskNumber = None

        for line in lines:
            primaryTaskMatch = re.match(r"^(\d+)\.\s(.+)", line)
            subTaskMatch = re.match(r"^\s+(\d+\.\d+\.?)\s(.+)", line)

            if primaryTaskMatch:
                taskNumber = primaryTaskMatch[1]
                taskText = primaryTaskMatch[2]
                currentTaskNumber = taskNumber

                newTasks.append(
                    {
                        "id": taskNumber,
                        "name": taskText,
                        "parent": "root",
                        "subtasks": [],
                    }
                )

            elif subTaskMatch:
                subTaskNumber = subTaskMatch[1]
                subTaskText = subTaskMatch[2]

                # Find parent task
                parentTask = next(
                    (task for task in newTasks if task["id"]
                     == currentTaskNumber), None
                )
                if parentTask:
                    parentTask["subtasks"].append(
                        {
                            "id": subTaskNumber,
                            "name": subTaskText,
                            "parent": currentTaskNumber,
                        }
                    )

        # Save tasks

        # Function for Parsing Tasks
        def parseTask(task: dict, parentID: str, projectID: str):
            taskData, _ = TasksAPIView.createTasks(
                {"projectID": projectID, "parentTaskID": parentID,
                    "name": task["name"]}
            )

            if "subtasks" in task:
                for subtask in task["subtasks"]:
                    parseTask(subtask, taskData["id"], projectID)
            return taskData

        createdTasks = []

        # Create a root task if one does not exist
        rootID = None
        if len(newTasks) != 1:
            taskData, _ = TasksAPIView.createTasks(
                {"projectID": projectID, "name": projectName}
            )
            rootID = taskData["id"]
            createdTasks.append(taskData)

        for task in newTasks:
            taskData = parseTask(task, rootID, projectID)
            createdTasks.append(taskData)

        return createdTasks, status.HTTP_201_CREATED
