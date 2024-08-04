from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.db import IntegrityError


from .models import Profile
from .serializers import ProfileSerializer
from api.decorators import apiKeyRequired
from api.utils import getAuthorizationToken, decodeApiKey


from rest_framework import generics, permissions, serializers
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

class ProfileList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


# dispatch protects all HTTP requests coming in
@method_decorator(apiKeyRequired, name="dispatch")
class ProfilesAPIView(APIView):
    """
    Create, get, and update profiles.
    """

    def get(self, request):
        """
        Retrieves profiles information. Only profiles can access all their own data if they pass their id.
        Other profiles can access email, id, and username if they pass email or id.
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            The query parameters can be:
                - id (str): Filter profile by ID.
                - email (str): Filter profile by email.

        @return A Response object containing a JSON array of serialized profile objects that match the query parameters.
        If no profiles match the query, a 400 Bad Request response is returned.

        @example Javascript:
            // To fetch all profiles
            fetch('/api/v1/profiles');

            // To fetch a profile by ID
            fetch('/api/v1/profiles?id=1234');

            // To fetch a profile by email
            fetch('/api/v1/profiles?email=profile@example.com');
        """

        try:
            queryParams = request.query_params.dict()

            responseData, httpStatus = self.getProfiles(
                queryParams, getAuthorizationToken(request)
            )

            return Response(responseData, httpStatus)

        except Exception as e:
            return Response(
                {"message": f"Error getting profile details: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """
        Handles the POST request to create a new profile based on the provided body parameters.
        Requires 'apiToken' passed in auth header or cookies.

        @param {HttpRequest} request - The request object.
            Headers:
                - Content-Type: 'application/json'
            Body parameters:
                - email (str) [REQUIRED]: The email address of the profile.
                - firstName (str): The first name of the profile.
                - lastName (str): The last name of the profile.
                - username (str) [REQUIRED]: The username for the profile.
                - teamIDs (list[str]): List of team IDs the profile is associated with.

        @return {HttpResponse} - On success, returns a status of 200 and a JSON body containing the profile's details.


        @example JavaScript:
            fetch('quayside.app/api/v1/profiles/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: 'profile@example.com',
                    firstName: 'John',
                    lastName: 'Doe',
                    username: 'johndoe',
                    teamIDs: ['team1', 'team2']
                })
            });
        """
        if request.content_type != "application/json":
            return Response(
                {"error": "Invalid Content-Type. Use application/json."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        responseData, httpStatus = self.createProfile(request.data)

        return Response(responseData, httpStatus)

    def put(self, request):
        """
        Updates a single profile.
        Requires 'apiToken' passed in auth header or cookies. 


        @param {HttpRequest} request - The request object.
                @param {HttpRequest} request - The request object.
            The request body can contain:
                - id (str) [REQUIRED]
                - email (str): The email address of the profile.
                - firstName (str): The first name of the profile.
                - lastName (str): The last name of the profile.
                - username (str) : The username for the profile.
                - teamIDs (list[str]): List of team IDs the profile is associated with.


        @return: A Response object with the updated task data or an error message.

        @example javascript
            await fetch(`quayside.app/api/v1/profiles/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({id: '1234, name: 'Task2'},
            });

        """
        responseData, httpStatus = self.updateProfile(
            request.data, getAuthorizationToken(request)
        )
        return Response(responseData, status=httpStatus)

    @staticmethod
    def updateProfile(profileData, authorizationToken):
        """
        Service API function that can be called internally as well as through the API to update
        a profile based on input data.

        @param task_data      Dict for a single project dict or list of dicts for multiple tasks.
        @return      A tuple of (response_data, http_status).
        """
        if "id" not in profileData:
            return {
                "message": "Error: Parameter 'id' required"
            }, status.HTTP_400_BAD_REQUEST

        profileID = decodeApiKey(authorizationToken).get("profileID")
        print(f"profileID from APIKEY: {profileID}")
        if profileID != profileData["id"] and authorizationToken:
            return {
                "message": "Unauthorized to update that profile."
            }, status.HTTP_401_UNAUTHORIZED

        try:
            profile = Profile.objects.get(id=profileData["id"])
        except Profile.DoesNotExist:
            return None, status.HTTP_404_NOT_FOUND

        
        serializer = ProfileSerializer(data=profileData, instance=profile, partial=True)

        if serializer.is_valid():
            serializer.save()  # Updates profiles
            return serializer.data, status.HTTP_200_OK

        return serializer.errors, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def getProfiles(profileData, authorizationToken=None):
        """
        Service API function that can be called internally as well as through the API to get a profile.

        @param profileData      Dict of data for a single profile.
        @return      A tuple of (response_data, http_status).
        """

        if not isinstance(profileData, list):
            # If authorized profile is getting information about their self, return all data
            profileID = decodeApiKey(authorizationToken).get("profileID")
            if "id" in profileData and profileID == profileData["id"]:
                if not profileData.get("id") and not profileData.get("email"):
                    return {
                        "message": "ProfileID or email required."
                    }, status.HTTP_400_BAD_REQUEST
                profile = Profile.objects.filter(**profileData).first()
                serializedProfile = ProfileSerializer(profile).data
                return [serializedProfile], status.HTTP_200_OK

            profileData = [profileData]

        # Else return only id, email, and username
        profileIDs = [profile.get("id") for profile in profileData if profile.get("id")]
        emails = [profile.get("email") for profile in profileData if profile.get("email")]

        if not profileIDs and not emails:
            return {
                "message": "No valid profile IDs or emails provided."
            }, status.HTTP_400_BAD_REQUEST

        profiles = Profile.objects.filter(Q(id__in=profileIDs) | Q(email__in=emails))

        if not profiles:
            return {"message": "No profiles found."}, status.HTTP_404_NOT_FOUND
        serializedProfiles = []
        for profile in profiles:
            serializedProfile = ProfileSerializer(profile).data
            serializedProfiles.append(
                {
                    "id": serializedProfile.get("id"),
                    "email": serializedProfile.get("email"),
                    "username": serializedProfile.get("username"),
                }
            )
        return serializedProfiles, status.HTTP_200_OK

    @staticmethod
    def createProfile(profileData):
        """
        Service API function that can be called internally as well as through the API to create a profile

        @param profileData      Dict of data for a single profile.
        @return      A tuple of (response_data, http_status).
        """

        serializer = ProfileSerializer(data=profileData)

        try:
            serializer.is_valid(raise_exception=True)
            profile = Profile.objects.create(**serializer.validated_data)
            response_data = ProfileSerializer(profile).data
            return response_data, status.HTTP_201_CREATED

        except IntegrityError as e:
            error_message = str(e)
            if "email" in error_message:
                return {
                    "error": "Email address is already in use."
                }, status.HTTP_400_BAD_REQUEST
            #           elif 'username' in error_message:
            #               return Response({'error': 'Profilename is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

            return {
                "error": "Duplicate key error.",
                "details": error_message,
            }, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            return {
                "error": "Internal server error.",
                "details": str(e),
            }, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def getAuthenticatedProfile(profileData):
        """
        THIS SHOULD ONLY BE USED FOR AUTHORIZATION WHEN LOGGING IN. DO NOT MAKE THIS A PUBLIC ROUTE.

        @param profileData      Dict of data for a single profile. Must contain email
        @return      A tuple of (response_data, http_status).
        """

        if "email" not in profileData:
            return "Error: Parameter 'email' required", status.HTTP_400_BAD_REQUEST

        profile = Profile.objects.filter(email=profileData["email"]).first()

        if not profile:
            return {"message": "Profile not found."}, status.HTTP_404_NOT_FOUND

        serializedProfile = ProfileSerializer(profile).data
        return {
            "apiKey": serializedProfile.get("apiKey"),
            "id": serializedProfile.get("id"),
        }, status.HTTP_200_OK


    # @staticmethod
    # def updateApiKey(profileID):
    #     """
    #     THIS SHOULD ONLY BE USED ON THE WEBSITE SIDE ONCE THE USER LOGS IN. DO NOT MAKE THIS A PUBLIC ROUTE.
    #     Creates new API key for the user.

    #     @param profileID      User's ID.
    #     @return      A tuple of (response_data, http_status).
    #     """

    #     try:
    #         profile = Profile.objects.get(id=profileID)
    #     except Profile.DoesNotExist:
    #         return None, status.HTTP_404_NOT_FOUND

    #     apiToken = createEncodedApiKey(profileID)
    #     encryptedApiKey = encryptApiKey(apiToken)
        
    #     serializer = ProfileSerializer(data={'apiKey':encryptedApiKey}, instance=profile, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()  # Updates profiles
    #         return serializer.data, status.HTTP_200_OK

    #     return serializer.errors, status.HTTP_400_BAD_REQUEST
