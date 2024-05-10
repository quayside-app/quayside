from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from api.decorators import apiKeyRequired
from api.serializers import FeedbackSerializer
from api.models import Feedback
from api.utils import getAuthorizationToken, decodeApiKey


@method_decorator(
    apiKeyRequired, name="dispatch"
)  # dispatch protects all HTTP requests coming in
class FeedbackAPIView(APIView):
    """
    Create, get, and delete feedback.
    """

    def get(self, request):
        """
        Retrieves a list of Feedback objects from MongoDB, filtered based on query parameters
        provided in the request. Requires 'apiToken' passed in auth header or cookies to check
        if the user is an admin

        @param {HttpRequest} request - The request object.
            The query parameters can be:
                - id (objectID str) [REQUIRED]
                or
                - projectID (objectID str)
                or
                - taskID (objectID str)
                or
                - userID (objectID str)

        @return A Response object containing a JSON array of serialized  objects that
        match the query parameters.

        @example Javascript:
            fetch('quayside.app/api/v1/feedback?userIDs=1234');
        """
        responseData, httpStatus = self.getFeedback(
            request.query_params.dict(), getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def post(self, request):
        """
        Creates feedback. Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The request body can contain:
                - userID (objectID str) [OPTIONAL]
                - projectID (objectID str)
                - taskID (objectID str) [OPTIONAL]
        @param {str} authorizationToken - JWT authorization token.

        @return A Response object containing a JSON array of the created feedback object.

        @example javascript:

            fetch('quayside.app/api/v1/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ projectID: 'AF6927BF', taskID: 'AC6927BF' }),
            });

        """
        responseData, httpStatus = self.createFeedback(
            request.data, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    def delete(self, request):
        """
        Deletes a feedback object or list of feedbacks provided by a user or for a given project.
        Requires 'apiToken' passed in auth header or cookies to check if the user is an admin.

        @param {HttpRequest} request - The request object.
            The query parameters MUST be:
                - id (objectID str)
                or
                - projectID (objectID str)
                or
                - taskID (objectID str)
                or
                - userID (objectID str)

        @return: A Response object with a success or an error message.

        @example javascript:

            fetch(`/api/v1/projects?id=1234`, {
                method: 'DELETE',
            });
        """

        responseData, httpStatus = self.deleteFeedback(
            request.query_params, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    @staticmethod
    def getFeedback(feedbackData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to get
        project data based on input data.

        @param feedbackData      Dict for a singular feedback object.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        #TODO: use auth token to check if user is admin

        try:
            if len(feedbackData) > 1:
                return { "message": "Need to have ONLY a id, taskID, or projectID property." }, status.HTTP_400_BAD_REQUEST
            
            feedback_objs = []

            if "id" in feedbackData:
                feedback_objs = Feedback.objects.get(id=feedbackData["id"])
            elif "taskID" in feedbackData:
                feedback_objs = Feedback.objects.filter(taskID__all=feedbackData["taskID"], **feedbackData)
            elif "projectID" in feedbackData:
                feedback_objs = Feedback.objects.filter(projectID__all=feedbackData["projectID"], **feedbackData)

            if not feedback_objs:
                return {
                    "message": "No feedback was found or you do not have authorization."
                }, status.HTTP_400_BAD_REQUEST
            serializer = FeedbackSerializer(feedback_objs, many=True)
            return serializer.data, status.HTTP_200_OK
        except Exception as e:
            print("Error:", e)
            return {"message": e}, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def createFeedback(feedbackData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to create
        feedback based on input data.

        @param feedbackData      Dict for a single feedback dict.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        userID = decodeApiKey(authorizationToken).get("userID")
        if "userID" in feedbackData and feedbackData["userID"] != userID:
            return { "message": "Not authorized to delete feedback." }, status.HTTP_401_UNAUTHORIZED
        
        if isinstance(feedbackData, list):
            serializer = FeedbackSerializer(data=feedbackData, many=True)
        else:
            serializer = FeedbackSerializer(data=feedbackData)

        if serializer.is_valid():
            serializer.save()  # Save the feedback(s) to the database
            # Returns data including new primary key
            return serializer.data, status.HTTP_201_CREATED

        return {"message":serializer.errors}, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def deleteFeedback(feedbackData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to delete feedback.

        @param feedbackData      Dict for a singular feedback object
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        #TODO: make use auth token to check if user is admin
        if len(feedbackData) > 1:
            return { "message": "Need to have ONLY a id, taskID, or projectID property." }, status.HTTP_400_BAD_REQUEST
        
        numberObjectsDeleted:int = 0

        if "id" in feedbackData:
            numberObjectsDeleted = Feedback.objects.get(id=feedbackData["id"]).delete()
        elif "taskID" in feedbackData:
            numberObjectsDeleted = Feedback.objects.filter(taskID__all=feedbackData["taskID"], **feedbackData).delete()
        elif "projectID" in feedbackData:
            numberObjectsDeleted = Feedback.objects.filter(projectID__all=feedbackData["projectID"], **feedbackData).delete()
        elif "userID" in feedbackData:
            numberObjectsDeleted = Feedback.objects.filter(userID__all=feedbackData["userID"], **feedbackData).delete()

        if numberObjectsDeleted == 0:
            return { "message": "No associated feedback found." }, status.HTTP_404_NOT_FOUND

        return { "message": str(numberObjectsDeleted) + " associated feedback items deleted successfully" }, status.HTTP_200_OK
