from pymongo import MongoClient
from bson.objectid import ObjectId
import os

def run_script():
    # Connect to MongoDB
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    hostname = "quayside-cluster.ry3otj1.mongodb.net"
    database = "quayside"

    connection_string = f"mongodb+srv://{username}:{password}@{hostname}/{database}?retryWrites=true&w=majority"
    client = MongoClient(connection_string)
    db = client['quayside']

    # update examples
    # tasks = db.Task.find({"status": {"$exists": False}})
    # for task in tasks:
    #     db.Task.update_one(
    #         {"_id": task["_id"]},
    #         {"$unset": {"status": ""}}
    # )

    # # Check if any status IDs on a project are null and replace them with a generated ObjectId
    # projects = db.Project.find({"taskStatuses.id": None})
    # for project in projects:
    #     for task_status in project["taskStatuses"]:
    #         if task_status["id"] is None:
    #             task_status["id"] = ObjectId()
    #     db.Project.update_one(
    #         {"_id": project["_id"]},
    #         {"$set": {"taskStatuses": project["taskStatuses"]}}
    #     )

    client.close()

if __name__ == "__main__":
    run_script()