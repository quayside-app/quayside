import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv


load_dotenv()

username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")

hostname = "quayside-cluster.ry3otj1.mongodb.net"
database = "quayside"

connection_string = f"mongodb+srv://{username}:{password}@{hostname}/{database}?retryWrites=true&w=majority&tls=true&tlsCAFile={certifi.where()}"

# Connect to MongoDB
client = MongoClient(connection_string)

try:
    db = client.get_database()
    print(db.list_collection_names())
except Exception as e:
    print("Error:", e)