import os
from pymongo import MongoClient
import certifi

# Retrieve credentials and setup the connection string
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
hostname = "quayside-cluster.ry3otj1.mongodb.net"
database = "quayside"

connection_string = f"mongodb+srv://{username}:{password}@{hostname}/{database}?retryWrites=true&w=majority&tls=true&tlsCAFile={certifi.where()}"

# Connect to MongoDB
client = MongoClient(connection_string)

# Access the database
db = client[database]

# Example: List collections
collections = db.list_collection_names()
print(collections)
