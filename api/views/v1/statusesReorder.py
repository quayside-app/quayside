from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from api.decorators import apiKeyRequired
from api.serializers import ProjectSerializer
from api.views.v1.projects import ProjectsAPIView
from api.utils import getAuthorizationToken


@method_decorator(apiKeyRequired, name="dispatch")
class StatusesReorderAPIView(APIView):
    """
    Bulk-reorder Kanban columns for a project.
    """

    def put(self, request):
        """
        Reorders statuses by accepting an ordered list of status IDs.
        Rewrites 'order' fields to match the supplied sequence (1-based).

        @param {HttpRequest} request - The request object.
            The request body MUST contain:
                - projectID (objectID str)
                - orderedIds (list of objectID str) — all current status IDs in desired order

        @return: 200 on success, 400 if orderedIds doesn't match current status IDs exactly.

        @example javascript:
            await fetch('/api/v1/statuses/reorder/', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ projectID: '...', orderedIds: ['id3', 'id1', 'id2'] }),
            });
        """
        responseData, httpStatus = self.reorderStatuses(
            request.data, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    @staticmethod
    def reorderStatuses(reorderData, authorizationToken):
        """
        Service function to reorder statuses for a project.

        @param reorderData      Dict with 'projectID' and 'orderedIds'.
        @param authorizationToken      JWT authorization token.
        @return      A tuple of (response_data, http_status).
        """
        try:
            data, httpsCode = ProjectsAPIView.getProjects(
                {"id": reorderData["projectID"]}, authorizationToken
            )
            data = data[0]

            if httpsCode != status.HTTP_200_OK and httpsCode != status.HTTP_404_NOT_FOUND:
                return {"message": data.get("message", "Error")}, httpsCode

            if "taskStatuses" not in data or not data["taskStatuses"]:
                return {"message": "No status associated with project"}, status.HTTP_404_NOT_FOUND

            ordered_ids = [str(i) for i in reorderData.get("orderedIds", [])]
            current_ids = {str(s["id"]) for s in data["taskStatuses"]}

            if set(ordered_ids) != current_ids or len(ordered_ids) != len(current_ids):
                return (
                    {"message": "orderedIds must contain all current status IDs exactly once."},
                    status.HTTP_400_BAD_REQUEST,
                )

            id_to_stat = {str(s["id"]): s for s in data["taskStatuses"]}
            for i, status_id in enumerate(ordered_ids, start=1):
                id_to_stat[status_id]["order"] = i

            serializer = ProjectSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return {"message": "Column order updated."}, status.HTTP_200_OK
            return {"message": str(serializer.errors)}, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            print("Error:", e)
            return {"message": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
