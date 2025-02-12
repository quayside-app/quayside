import pytest
from rest_framework.exceptions import ValidationError
from api.models import Project, User
from api.serializers import ProjectSerializer, StatusSerializer
import mongoengine as mongo
from dotenv import load_dotenv
import os
import certifi
from pymongo import MongoClient
from mongoengine import connect, disconnect
import django
from bson import ObjectId  # Ensure ObjectId is imported if needed

django.setup()


load_dotenv()

MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

hostname = "quayside-cluster.ry3otj1.mongodb.net"
database = "quayside"

connection_string = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{hostname}/{database}?retryWrites=true&w=majority&tls=true&tlsCAFile={certifi.where()}"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quayside.settings")
@pytest.fixture(scope="session")
def setup_database():
    # Connect to MongoDB
    connect(db=database, host=connection_string)
    yield  # Pass the database instance to tests

    # Cleanup: Close connection after tests
    disconnect()
    # Create an initial project with valid ObjectId
    initial_project_data = {
        'name': "Test Project",
        'description': "This is a test project.",
        'userIDs': [str(ObjectId())],  # Ensure a valid ObjectId as a string
        'taskStatuses': [{
            'status': 'In Progress',
            'task': 'Test Task',
            'name': 'Development',  # Include required 'name' field
            'color': '#FF5733',     # Include required 'color' field
        }],
    }

    # Serialize and validate project data
    project_serializer = ProjectSerializer(data=initial_project_data)
    assert project_serializer.is_valid(), project_serializer.errors  # Ensuring validation passes

    # Save the project instance
    project = project_serializer.save()

    # Data for updating the project
    updated_data = {
        'name': "Updated Test Project",
        'description': "This is an updated test project.",
        'taskStatuses': [{
            'status': 'Completed',
            'task': 'Test Task',
            'name': 'Testing',   # Required field
            'color': '#33FF57',  # Required field
        }],
    }

    # Update the project with new data
    update_serializer = ProjectSerializer(instance=project, data=updated_data)
    assert update_serializer.is_valid(), update_serializer.errors  # Ensuring validation passes

    updated_project = update_serializer.save()

    # Assertions to check if the update was successful
    assert updated_project.name == "Updated Test Project"
    assert updated_project.description == "This is an updated test project."
    assert len(updated_project.taskStatuses) == 1
    assert updated_project.taskStatuses[0]['status'] == "Completed"
    assert updated_project.taskStatuses[0]['task'] == "Test Task"
    assert updated_project.taskStatuses[0]['name'] == "Testing"
    assert updated_project.taskStatuses[0]['color'] == "#33FF57"

# @pytest.mark.django_db
def test_update_project_with_invalid_task_status():
    # Create an initial project with a valid ObjectId
    initial_project_data = {
        'name': "Test Project",
        'description': "This is a test project.",
        'userIDs': [str(ObjectId())],  # Ensure a valid ObjectId as a string
        'taskStatuses': [{
            'status': 'In Progress',
            'task': 'Test Task',
            'name': 'Development',  # Required field
            'color': '#FF5733',     # Required field
            'order': 1,             # Required field
        }],
    }

    # Serialize and save the initial project
    project_serializer = ProjectSerializer(data=initial_project_data)
    assert project_serializer.is_valid(), project_serializer.errors
    project = project_serializer.save()

    # Invalid task status data (missing 'task' field)
    invalid_data = {
        'taskStatuses': [{
            'status': 'Completed',
            'name': 'Testing',   # Required field
            'color': '#33FF57',  # Required field
            'order': 2,          # Required field
            # 'task' field is missing here
        }],
    }

    # Try updating the project with invalid data
    update_serializer = ProjectSerializer(instance=project, data=invalid_data)

    # Manually check if the validation fails and errors are raised
    is_valid = update_serializer.is_valid()
    assert not is_valid, "The serializer should not be valid"
    assert 'taskStatuses' in update_serializer.errors, "taskStatuses field errors are missing"
    assert 'task' in update_serializer.errors['taskStatuses'][0], "'task' field error is missing"
# @pytest.mark.django_db
def test_update_project_with_no_task_statuses():
    # Create a valid ObjectId as a string for userIDs
    valid_user_id = str(ObjectId())

    # Create an initial project with valid taskStatuses data
    initial_project_data = {
        'name': "Test Project",
        'description': "This is a test project.",
        'userIDs': [valid_user_id],  # Ensure userIDs is a list with valid ObjectId
        'taskStatuses': [{
            'status': 'In Progress',
            'task': 'Test Task',
            'name': 'Development',  # Add required 'name'
            'color': '#FF5733',     # Add required 'color'
            'order': 1,             # Add required 'order'
        }],
    }

    # Serialize and save the initial project
    project_serializer = ProjectSerializer(data=initial_project_data)
    assert project_serializer.is_valid(), project_serializer.errors
    project = project_serializer.save()

    # Update the project with no task statuses (removing taskStatuses field)
    updated_data = {
        'name': "Updated Test Project",
        'description': "This is an updated test project.",
        'taskStatuses': [],  # Empty list for taskStatuses
    }

    # Update the project with the new data
    update_serializer = ProjectSerializer(instance=project, data=updated_data)

    # Manually check if the validation is correct
    is_valid = update_serializer.is_valid()
    assert is_valid, f"Validation failed: {update_serializer.errors}"

    updated_project = update_serializer.save()

    # Check if the taskStatuses field was cleared
    assert updated_project.name == "Updated Test Project"
    assert updated_project.description == "This is an updated test project."
    assert updated_project.taskStatuses == [], "taskStatuses should be an empty list"
