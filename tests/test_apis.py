import pytest
from rest_framework.exceptions import ValidationError
from api.models import Project, User
from api.serializers import ProjectSerializer, StatusSerializer

@pytest.mark.django_db
def test_update_project_with_task_statuses():
    # Create a user instance
    user = User.objects.create(name="Test User")

    # Create an initial project
    initial_project_data = {
        'name': "Test Project",
        'description': "This is a test project.",
        'userIDs': [user.id],
        'taskStatuses': [{'status': 'In Progress', 'task': 'Test Task'}],
    }

    # Serialize and save the initial project
    project_serializer = ProjectSerializer(data=initial_project_data)
    project_serializer.is_valid(raise_exception=True)
    project = project_serializer.save()

    # Data for updating the project
    updated_data = {
        'name': "Updated Test Project",
        'description': "This is an updated test project.",
        'taskStatuses': [{'status': 'Completed', 'task': 'Test Task'}],
    }

    # Update the project with the new data
    update_serializer = ProjectSerializer(instance=project, data=updated_data)
    update_serializer.is_valid(raise_exception=True)
    updated_project = update_serializer.save()

    # Check if the project fields are updated correctly
    assert updated_project.name == "Updated Test Project"
    assert updated_project.description == "This is an updated test project."
    assert len(updated_project.taskStatuses) == 1
    assert updated_project.taskStatuses[0].status == "Completed"
    assert updated_project.taskStatuses[0].task == "Test Task"

@pytest.mark.django_db
def test_update_project_with_invalid_task_status():
    # Create a user instance
    user = User.objects.create(name="Test User")

    # Create an initial project
    initial_project_data = {
        'name': "Test Project",
        'description': "This is a test project.",
        'userIDs': [user.id],
        'taskStatuses': [{'status': 'In Progress', 'task': 'Test Task'}],
    }

    # Serialize and save the initial project
    project_serializer = ProjectSerializer(data=initial_project_data)
    project_serializer.is_valid(raise_exception=True)
    project = project_serializer.save()

    # Invalid task status data (missing 'task' field)
    invalid_data = {
        'taskStatuses': [{'status': 'Completed'}],  # Missing 'task'
    }

    # Try updating the project with invalid data
    update_serializer = ProjectSerializer(instance=project, data=invalid_data)
    with pytest.raises(ValidationError):
        update_serializer.is_valid(raise_exception=True)

@pytest.mark.django_db
def test_update_project_with_no_task_statuses():
    # Create a user instance
    user = User.objects.create(name="Test User")

    # Create an initial project
    initial_project_data = {
        'name': "Test Project",
        'description': "This is a test project.",
        'userIDs': [user.id],
        'taskStatuses': [{'status': 'In Progress', 'task': 'Test Task'}],
    }

    # Serialize and save the initial project
    project_serializer = ProjectSerializer(data=initial_project_data)
    project_serializer.is_valid(raise_exception=True)
    project = project_serializer.save()

    # Update the project with no task statuses (removing taskStatuses field)
    updated_data = {
        'name': "Updated Test Project",
        'description': "This is an updated test project.",
        'taskStatuses': [],  # Empty list for taskStatuses
    }

    # Update the project with the new data
    update_serializer = ProjectSerializer(instance=project, data=updated_data)
    update_serializer.is_valid(raise_exception=True)
    updated_project = update_serializer.save()

    # Check if the taskStatuses field was cleared
    assert updated_project.name == "Updated Test Project"
    assert updated_project.description == "This is an updated test project."
    assert updated_project.taskStatuses == []

