import os
import jwt
from dotenv import load_dotenv
from api.views.v1.users import UsersAPIView

def global_context(request):
    """
    Sets context variables used by EVERY HTML template.
    Currently sets the userID and api version url.

    @param {HttpRequest} request - The request object.
    @returns {dict} - A dictionary with the API URL and the user ID,
        where the user ID is an empty string if not authenticated.
    """

    # Get userID from jwt if they are logged in
    load_dotenv()
    secretKey = os.getenv("API_SECRET")
    token = request.COOKIES.get("apiToken")

    if token:
        decoded = jwt.decode(token, secretKey, algorithms=["HS256"])
        userID = decoded.get("userID")
        username = UsersAPIView.getUser({"id": userID})[0].get("user").get("username")
    else:
        userID = ""

    return {"apiUrl": "/api/v1", "userID": userID, 'username': username}
