from django.http import JsonResponse
import jwt
from api.models import User


from api.utils import decodeApiKey, decryptApiKey


def apiKeyRequired(function):
    """
    Citation: ChatGPT

    Allows token to be passed in the authorization header OR through cookies (header good for scripts,
    cookies good for websites).
    """
    def wrap(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')

        # Try cookies if there is not a token in the header
        if not token:
            token = request.COOKIES.get('apiToken')

        # If no token anywhere, raise an error
        if not token:
            return JsonResponse({'Error': 'No token provided'}, status=401)

        try:
            decodedKey = decodeApiKey(token)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'Error': 'API Key is expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'Error': 'Invalid API Key'}, status=401)

        # Verify that the user is in the database + API key matches (Can check perms if needed too)
        userID = decodedKey.get("userID")
        try:
            # TODO USE user route instead!!!
            user = User.objects.filter(id=userID).first()

            if not user:
                return JsonResponse({'Error': 'No user associated with that token'}, status=401)

            # Check API keys match
            decryptedApiToken = decryptApiKey(user["apiKey"])
            if token != decryptedApiToken:
                return JsonResponse({'Error': 'No user associated with that token'}, status=401)
            
        except Exception as e:
            return JsonResponse({'Error': 'Could not find user associated with token'}, status=401)
        return function(request, *args, **kwargs)  # Call original function
    return wrap
