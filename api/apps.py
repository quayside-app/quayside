import os
from django.apps import AppConfig
import mongoengine as mongo
from dotenv import load_dotenv



class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        """
        Ran when app starts. Sets up database connection.
        """
        self.connect_database()

    def connect_database(self):
        """
        Establishes a connection to the MongoDB database using environment variables. Requires
        an .env file with MONGO_USERNAME and MONGO_PASSWORD variables. Adjust hostname and
        database name as necessary for different setups.
        """

        # Load environment variables from .env file
        load_dotenv()
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        hostname = "quayside-cluster.ry3otj1.mongodb.net"
        database = "quayside"

        connection_string = f"mongodb+srv://{username}:{password}@{hostname}/{database}?retryWrites=true&w=majority"
        mongo.connect(db=database, host=connection_string)
