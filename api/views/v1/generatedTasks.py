from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import GeneratedTaskSerializer
from dotenv import load_dotenv
import os
from openai import OpenAI
import re


class GeneratedTasks(APIView):
    """
    Generates and saves tasks with ChatGPT
    """

    def post(self, request):
        serializer = GeneratedTaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        userDescription = serializer.validated_data.description

        # Load ChatGPT creds
        load_dotenv()
        chatGPTAPIKey = os.getenv('CHATGPT_API_KEY')

        # Call ChatGPT
        client = OpenAI(apiKey=chatGPTAPIKey)
        completion = client.chat.completions.create(
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
                {"role": "user", "content": userDescription}
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
                    parentTask.subtasks.push({
                        "id": subTaskNumber,
                        "name": subTaskText,
                        "parent": currentTaskNumber
                    })
        print(newTasks)