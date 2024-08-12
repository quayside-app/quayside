from django.http import JsonResponse
import jwt
from apiAccounts.models import Profile
from api.utils import decodeApiKey, decryptApiKey, getAuthorizationToken


def apiKeyRequired(function):
    """
    Wraps function to authenticate it.
    Requires authorization token to be passed in the authorization header OR through cookies (header good for scripts,
    cookies good for websites).

    @param function Function to be wrapped.
    """

    def wrap(request, *args, **kwargs):

        token = getAuthorizationToken(request)

        # If no token anywhere, raise an error
        if not token:
            return JsonResponse({"Error": "No token provided"}, status=401)

        try:
            decodedKey = decodeApiKey(token)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"Error": "API Key is expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"Error": "Invalid API Key"}, status=401)

        # Verify that the user is in the database + API key matches (Can check perms if needed too)
        profileID = decodedKey.get("profileID")
        try:

            user = Profile.objects.filter(id=profileID).first()

            if not user:
                return JsonResponse(
                    {"Error": "No user associated with that token"}, status=401
                )

            # Check API keys match
            decryptedApiToken = decryptApiKey(user.apiKey)
            if token != decryptedApiToken:
                return JsonResponse(
                    {"Error": "No user associated with that token"}, status=401
                )

        except Exception as e:
            return JsonResponse(
                {"Error" : f"Could not find user associated with token: {e}"}, status=401
            )
        return function(request, *args, **kwargs)  # Call original function

    return wrap
