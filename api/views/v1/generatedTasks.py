# import os
# import re
# import sys
# from dotenv import load_dotenv
# import openai
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils.decorators import method_decorator

# from api.serializers import GeneratedTaskSerializer
# from api.views.v1.tasks import TasksAPIView
# from api.decorators import apiKeyRequired
# from api.utils import getAuthorizationToken


# # Dispatch protects all HTTP requests coming in
# @method_decorator(apiKeyRequired, name="dispatch")
# class GeneratedTasksAPIView(APIView):
#     """
#     Generates and saves tasks with ChatGPT. Requires apiKey.
#     """

#     def post(self, request):
#         """
#         Generate and saves tasks for a project.
#         Requires 'apiToken' passed in auth header or cookies.

#         @param {HttpRequest} request - The request object.
#             The request body should include:
#             - name: A string with the name/description of the project.
#             - projectID: A string of the project ID.

#         @returns {Response} - A Response object containing a JSON array of serialized Task objects.


#         @example Javascript:

#             fetch('quayside.app/api/v1/GeneratedTasks', {
#                 method: 'POST',
#                 headers: { 'Content-Type': 'application/json' },
#                 body: JSON.stringify({ name: 'New Project', projectID: '12345' }),
#             });
#         """
#         responseData, httpStatus = self.generateTasks(
#             request.data, getAuthorizationToken(request)
#         )
#         return Response(responseData, status=httpStatus)

#     @staticmethod
#     def generateTasks(projectData, authorizationToken):
#         """
#         Service API function that can be called internally as well as through the API to generate
#         and save tasks.
#         @param {dict} projectData -  Requires 'name' and 'projectID' keys.
#         @param authorizationToken      JWT authorization token.
#         @returns {tuple} - A tuple containing the list of created tasks and the HTTP status code.
#         """

#         # Check
#         serializer = GeneratedTaskSerializer(data=projectData)
#         if not serializer.is_valid():
#             return {"message":serializer.errors}, status.HTTP_400_BAD_REQUEST

#         projectName = serializer.validated_data["name"]
#         projectID = serializer.validated_data["projectID"]
#         projectDescription = serializer.validated_data["description"]
#         totalProjectMinutes = 0

#         # Load ChatGPT creds
#         load_dotenv()
#         openai.api_key = os.getenv("CHATGPT_API_KEY")

#         # Call ChatGPT
#         completion = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": """You are an assistant for quayside.app, a project management team. 
#                     You are given as input a project or task that a single person or a team 
#                     wants to take on. Divide the task into less than 5 subtasks and list them 
#                     hierarchically in the format where task 1 has subtasks 1.1, 1.2,...
#                     and task 2 has subtasks 2.1, 2.2, 2.3,... and so forth and allow for subtasks to 
#                     have their own hierarcy in the format of 1.1.1, 1.1.2, 1.13,... and so forth. For each subtask without it's own hierarcy, 
#                     provide a time estimation in minutes in square brackets with the label "minutes". Do not give a minute range.
#                     Make sure that every task is on one line after the number and has a time estimation. 
#                     NEVER create new paragraphs within a task or subtask.
#                     """,
#                 },
#                 {"role": "user", "content": f"Project Name: {projectName}\nProject Description: {projectDescription}"},
#             ],
#             temperature=0,
#             max_tokens=1024,
#             top_p=1,
#             frequency_penalty=0,
#             presence_penalty=0,
#         )

#         generatedString = completion.choices[0].message.content


#         # Parse response into tasks with durations
#         newTasks = []
#         lines = generatedString.split("\n")

#         degreeOfSeparation = 1
#         subtasks = []

#         for line in reversed(lines):
#             strDuration = re.search(r"\[(\d+(?:\.\d+)?)\s*(minute|hour|day|week)(?:s)?\]", line) # parses duration from text between brackets returned by OpenAI

#             # minimum minutes
#             durationMinutes = 0
#             if strDuration:
#                 line = line[0 : line.rfind(" [")]

#             primaryTaskMatch = re.match(r"^(\d+)\.\s(.+)", line)
#             subTaskMatch = re.match(r"^\s+(\d+\.(\d+|\d+\.)+)?\s(.+)", line)
            
#             if strDuration:
#                 type = strDuration.group(2)

#                 if type.find("week") != -1:
#                     durationMinutes = int(5 * 8 * 60 * float(strDuration.group(1)))
#                 elif type.find("day") != -1:
#                     durationMinutes = int(8 * 60 * float(strDuration.group(1)))
#                 elif type.find("hour") != -1:
#                     durationMinutes = int(60 * float(strDuration.group(1)))
#                 else:
#                     durationMinutes = int(strDuration.group(1))

#             if primaryTaskMatch or subTaskMatch:
#                 allTaskNumbers = (subTaskMatch[1] if subTaskMatch else primaryTaskMatch[1]).split(".")

#                 if (allTaskNumbers[-1] == ""):
#                     allTaskNumbers.pop(-1)

#             if subTaskMatch:
#                 if degreeOfSeparation == 1:
#                     degreeOfSeparation = len(allTaskNumbers)

#                 subTaskText = subTaskMatch[3]
                
#                 currentSubtask = {
#                     "id": allTaskNumbers[-1],
#                     "name": subTaskText,
#                     "parent": allTaskNumbers[-2],
#                     "durationMinutes": durationMinutes
#                 }

#                 if degreeOfSeparation > len(allTaskNumbers) or degreeOfSeparation == 1:
#                     degreeOfSeparation = len(allTaskNumbers) # aka degreeOfSeparation -= 1

#                     totalMinutes = 0
#                     for task in subtasks:
#                         totalMinutes += task["durationMinutes"]

#                     currentSubtask["durationMinutes"] = totalMinutes
#                     currentSubtask["subtasks"] = subtasks[:]
#                     subtasks.clear()

#                 subtasks.insert(0, currentSubtask)
                    
#             elif primaryTaskMatch:
#                 taskText = primaryTaskMatch[2]

#                 totalMinutes = 0
#                 for task in subtasks:
#                     totalMinutes += task["durationMinutes"]
                    
#                 totalProjectMinutes += totalMinutes if totalMinutes > 0 else durationMinutes
                
#                 newTasks.insert(0, 
#                     {
#                         "id": allTaskNumbers[0],
#                         "name": taskText,
#                         "parent": "root",
#                         "durationMinutes": totalMinutes if totalMinutes > 0 else durationMinutes,
#                         "subtasks": subtasks[:],
#                     }
#                 )

#                 subtasks.clear()

#         # Save tasks

#         # Function for Parsing Tasks. TODO: do this in 1 db write??
#         def parseTask(task: dict, parentID: str, projectID: str):
#             data, httpsCode = TasksAPIView.createTasks(
#                 {
#                     "projectID": projectID,
#                     "parentTaskID": parentID,
#                     "name": task["name"],
#                     "durationMinutes": task["durationMinutes"]
#                 },
#                 authorizationToken,
#             )
#             if httpsCode != status.HTTP_201_CREATED:
#                 return data, httpsCode
#             taskData = data[0]
#             if "subtasks" in task:
#                 for subtask in task["subtasks"]:
#                     parseTask(subtask, taskData["id"], projectID)
#             return taskData

#         createdTasks = []

#         # Create a root task if one does not exist
#         rootID = None
#         if len(newTasks) != 1:
#             data, httpsCode = TasksAPIView.createTasks(

#                 {"projectID": projectID, "name": projectName, "durationMinutes": totalProjectMinutes}, authorizationToken

#             )
#             if httpsCode != status.HTTP_201_CREATED:
#                 return data, httpsCode
#             taskData = data[0]

#             rootID = taskData["id"]
#             createdTasks.append(taskData)

#         for task in newTasks:
#             taskData = parseTask(task, rootID, projectID)
#             createdTasks.append(taskData)

#         return createdTasks, status.HTTP_201_CREATED
