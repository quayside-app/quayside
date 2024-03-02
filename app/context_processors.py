import jwt
from dotenv import load_dotenv
import os

def global_context(request):
    """
    Sets context used by EVERY html template
    """

    # Get userID from jwt if they are logged in
    # Could just store ID in cookies instead maybe?
    load_dotenv()
    secretKey = os.getenv('API_SECRET')
    token = request.COOKIES.get('apiToken')
    decoded = jwt.decode(token, secretKey, algorithms=["HS256"])
    userID = decoded.get("userID")
    print(userID)

    if not userID:
        userID = ""
    return {'api_url': '/api/v1',
            'userID': userID}
        
    