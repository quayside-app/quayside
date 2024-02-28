from django.http import JsonResponse
import jwt
from dotenv import load_dotenv
import os
from api.models import User


def api_key_required(function):
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
            print("TOKEN HERE:", token)

        # If no token anywhere, raise an error
        if not token:
            return JsonResponse({'Error': 'No token provided'}, status=401)
        
        load_dotenv()
        secretKey = os.getenv('API_SECRET')

        try:
            decoded = jwt.decode(token, secretKey, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'Error': 'Token is expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'Error': 'Invalid token'}, status=401)

        # Verify that the user is in the database (Can check perms if needed too)
        userID = decoded.get("userID")
        print("decorator userID:", userID)
        try:
            # TODO USE user route instead!!!
            user = User.objects.filter(id=userID).first()
            if not user:
                return JsonResponse({'Error': 'No user associated with that token'}, status=401)
        except Exception as e:
            return JsonResponse({'Error': 'Could not find user associated with token'}, status=401)
        return function(request, *args, **kwargs)  # Call original function
    return wrap
