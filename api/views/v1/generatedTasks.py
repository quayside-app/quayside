from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import GeneratedTaskSerializer
from dotenv import load_dotenv
import os
import openai 
import re

class GeneratedTasks(APIView):
    """
    Generates and saves tasks with ChatGPT
    """

    def post(self, request):
        response_data, http_status = self.generateTasks(request.data) 
        return Response(response_data, status=http_status)


    @staticmethod
    def generateTasks(projectData):
        """
        Service API function that can be called internally as well as through the API to generate 
        and save tasks.
        """
        print("HERE1")
        #! TODO needs authorization - pass API key?

        # Check
        serializer = GeneratedTaskSerializer(data=projectData)
        if not serializer.is_valid():
            print(serializer.errors)
            return serializer.errors, status.HTTP_400_BAD_REQUEST

        # Load ChatGPT creds
        load_dotenv()
        openai.api_key = os.getenv('CHATGPT_API_KEY')

        # Call ChatGPT
        # TODO add exception handleing
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content":
                    """You are an assistant for quayside.app, a project management team. 
                    You are given as input a project or task that a single person or a team 
                    wants to take on. Divide the task into less than 5 subtasks and list them 
                    hierarchically in the format where task 1 has subtasks 1.1, 1.2,...
                    and task 2 has subtasks 2.1, 2.2, 2.3,... and so forth. Make sure that every 
                    task is on one line after the number. NEVER create new paragraphs within a 
                    task or subtask.
                    """
                    },
                {"role": "user", "content": serializer.validated_data["description"]}
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        generatedString = completion.choices[0].message.content

        # Parse response into tasks
        newTasks = []
        lines = generatedString.split("\n")

        currentTaskNumber = None

        for line in lines:
            primaryTaskMatch = re.match(r'^(\d+)\.\s(.+)', line)
            subTaskMatch = re.match(r'^\s+(\d+\.\d+\.?)\s(.+)', line)

            if primaryTaskMatch:
                taskNumber =  primaryTaskMatch[1]
                taskText = primaryTaskMatch[2]
                currentTaskNumber = taskNumber

                newTasks.append({
                    "id": taskNumber,
                    "name": taskText,
                    "parent": "root",
                    "subtasks": []
                })
            
            elif subTaskMatch:
                subTaskNumber = subTaskMatch[1]
                subTaskText = subTaskMatch[2]

                # Find parent task
                parentTask = next((task for task in newTasks if task['id'] == currentTaskNumber), None)
                if parentTask:
                    parentTask['subtasks'].append({
                        "id": subTaskNumber,
                        "name": subTaskText,
                        "parent": currentTaskNumber
                    })
        
        
        print(newTasks)
        return

        # Create a root task if one does not exist
        if newTasks.length != 1:
            pass


        # Parse tasks and save them
        # serializer.validated_data["projectID"],
        #! TODO return stuff
            