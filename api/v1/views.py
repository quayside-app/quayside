import requests
import urllib.parse

from rest_framework.decorators import api_view, action
from rest_framework.response import Response 
from rest_framework import status, views, viewsets
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate


from django.conf import settings

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from oauthlib.oauth2 import WebApplicationClient as WAC


from .models import User
#from .serializers import UserSerializer, ProfileSerializer


class AccountLogin:

    def post(request):
        """
        Login with Oauth
        
        @param {HttpRequest} request - The request object.
        The query parameters can be:
            - provider (str): Either "Google" or "Github"
            - email (str): Filter user by email.
        """
        try:
            provider = request.data.get('provider')
            
            clientID = ""
            authorizationUrl = ""
            providerScope = []
            if provider == "GitHub":
                clientID = settings.GITHUB_CLIENT_ID
                authorizationUrl = "https://github.com/login/oauth/authorize"
                providerScope = ["user"]

            elif provider == "Google":
                clientID = settings.GOOGLE_CLIENT_ID
                authorizationUrl = "https://accounts.google.com/o/oauth2/v2/auth"
                providerScope = [
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "https://www.googleapis.com/auth/userinfo.email",
                ]
            else:
                return Response( {"message": "Unsupported oauth provider"}, 
                                status=status.HTTP_400_BAD_REQUEST)


            client = WAC(clientID)

            url = client.prepare_request_uri(
                authorizationUrl,
                redirect_uri=settings.REDIRECT_URI,
                scope=providerScope,
                state="test",
            )
            return HttpResponseRedirect(url)  ## TODO: Is this correct?

        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        



class OauthCallback(views.APIView):
    def get(self, request):
        """
        Handles the callback after GitHub authentication, creates the user in the db if they
        don't exist, and retrieves the user's info and API key (generating it if it doesn't exist).
        It then saves the API key to the user's cookies so it can be sent to the API routes in
        future requests.

        @param request: The HTTP request object containing the callback data from GitHub or Google.
        @returns: The rendered index.html page with the API token set in the cookies.
        """
        print(self.request)
        data = self.request.GET
        authcode = data["code"]
        try:
            provider = self.request.session['provider']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # state = data["state"]

        # Get API token
        if provider == "GitHub":
            token_url = "https://github.com/login/oauth/access_token"
            clientID = settings.GITHUB_CLIENT_ID
            clientSecret = settings.GITHUB_CLIENT_SECRET
            username = "login"
            apiRequestURL = settings.GITHUB_API_URL_USER

        elif provider == "Google":
            token_url = "https://accounts.google.com/o/oauth2/token"
            clientID = settings.GOOGLE_CLIENT_ID
            clientSecret = settings.GOOGLE_CLIENT_SECRET
            username = "name"
            apiRequestURL = settings.GOOGLE_API_URL_USER_PROFILE
        client = WAC(clientID)

        data = client.prepare_request_body(
            code=authcode,
            redirect_uri=settings.REDIRECT_URI,
            client_id=clientID,
            client_secret=clientSecret,
        )

        if provider == "Google":  # caters request and header to google specifications
            data = dict(urllib.parse.parse_qsl(data))
            response = requests.post(token_url, json=data, timeout=10)
            client.parse_request_body_response(response.text)
            header = {"Authorization": f"Bearer {client.token['access_token']}"}
        else:  # caters to GitHub specifications
            response = requests.post(token_url, data=data, timeout=10)
            client.parse_request_body_response(response.text)
            header = {"Authorization": f"token {client.token['access_token']}"}

        response = requests.get(apiRequestURL, headers=header, timeout=10)

        oauthUserInfo = response.json()

        # For Github, if user has no visible email, make second request for email
        if not oauthUserInfo.get("email"):
            response = requests.get(
                settings.GITHUB_API_URL_EMAIL, headers=header, timeout=10
            )
            oauthUserInfo["email"] = response.json()[0]["email"]

        # Create a user in our db if none exists
        if oauthUserInfo.get("username"):
            username = oauthUserInfo.get("username")
        else:
            username = oauthUserInfo.get("email").split("@")[0]

        if not User.objects.filter(email=oauthUserInfo.get("email")).exists():
            names = oauthUserInfo.get("name", "quayside user").split()

            userInfo, httpsCode = UsersAPIView.createUser(
                {
                    "email": oauthUserInfo.get("email"),
                    "username": username,
                    "firstName": names[0],
                    "lastName": names[-1],
                }
            )

        # Redirect instead of rendering (to make it update)
        response = redirect("/")

        apiToken = userInfo.get("apiKey")  # Get API key

        if apiToken:
            apiToken = decryptApiKey(apiToken)
        # Create an api key if it doesn't exist in the db yet
        else:
            # Create/encrypt API key
            apiToken = createEncodedApiKey(userInfo["id"])
            encryptedApiKey = encryptApiKey(apiToken)

            message, httpsCode = UsersAPIView.updateUser(
                {
                    "id": userInfo["id"],
                    "apiKey": encryptedApiKey,
                },
                apiToken,
            )
            if httpsCode != status.HTTP_200_OK:
                print(f"User update failed: {message}")
                return HttpResponseServerError(f"An error occurred: {message}")

        # Save api key to cookies
        # Setting httponly is safer and doesn't let the key be accessed by js (to prevent xxs).
        # Instead the browser will always pass the cookie to the server.
        response.set_cookie("apiToken", apiToken, httponly=True)

        # Make sure to add email not created already (oath doesn't require username I think but does require email)
        if "username" not in userInfo or not userInfo["username"]:
            message, httpsCode = UsersAPIView.updateUser(
                {
                    "id": userInfo["id"],
                    "username": username,
                },
                apiToken,
            )
            if httpsCode != status.HTTP_200_OK:
                print(f"User update failed: {message}")
                return HttpResponseServerError(f"An error occurred: {message}")

        return response
