import jwt
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os

def createEncodedApiKey(userID: str) -> str:
    """
    Generates an encoded API key for a given user ID using JWT encoding. 
    WARNING: if this key is stored in the database, it still needs to be encrypted (below).

    @param userID: The user ID for to encode.
    @return: The encoded API key for the user
    """

    load_dotenv()
    secretKey = os.getenv('API_SECRET')
    payload = {
        "userID": userID,
    }

    encodedApiKey = jwt.encode(payload, secretKey, algorithm="HS256")
    return encodedApiKey

def decodeApiKey(apiKey:str) -> str:
    """
    Decodes the provided API key using JWT decoding to proved the userID.
    Will raise jwt.ExpiredSignatureError, or jwt.InvalidTokenError if the token is expired or invalid.

    @param apiKey: The encoded API key that needs to be decoded.
    @return: The decoded API key.

    @example: 
        userID = decodeApiKey("1234").get("userID")
    """
    load_dotenv()
    secretKey = os.getenv('API_SECRET')

    decodedApiKey = jwt.decode(apiKey, secretKey, algorithms=["HS256"])

    return decodedApiKey

def encryptApiKey(apiKey:str) -> str:
    """
    Encrypts the provided API key using Fernet symmetric encryption. 

    @param apiKey: The unencrypted API key to be encrypted.
    @return: The encrypted API key as a string.
    """
    fernetSecretKey = os.getenv('API_SECRET') + "=" # .Env does NOT read "=" properly but fernet requires it
    fernet = Fernet(fernetSecretKey.encode())
    encryptedApiKey = fernet.encrypt(apiKey.encode()).decode()
    
    return encryptedApiKey


def decryptApiKey(apiKey:str) -> str:
    """
    Decrypts the provided encrypted API key using Fernet symmetric encryption.

    @param apiKey: The encrypted API key that needs to be decrypted.
    @return: The decrypted API key as a string (still is encoded w/ jwt).
    """
    fernetSecretKey = os.getenv('API_SECRET') + "=" # .Env does NOT read "=" properly but fernet requires it
    fernet = Fernet(fernetSecretKey.encode())
    decryptedApiKey = fernet.decrypt(apiKey).decode()
    
    return decryptedApiKey

