from unittest.mock import MagicMock, patch
from django.test import SimpleTestCase
from bson import ObjectId

from api.serializers import ProjectSerializer


class TestProjectSerializerStructure(SimpleTestCase):
    """Basic sanity checks on ProjectSerializer that don't need a real DB."""

    def test_serializer_has_required_methods(self):
        self.assertTrue(hasattr(ProjectSerializer, "Meta"))
        self.assertTrue(hasattr(ProjectSerializer, "create"))
        self.assertTrue(hasattr(ProjectSerializer, "update"))

    @patch("api.models.Project.Status")
    def test_update_replaces_not_appends_statuses(self, MockStatus):
        """
        ProjectSerializer.update() must replace taskStatuses, not append.
        Regression: the old implementation appended status_data_list onto
        instance.taskStatuses each time update() was called, so calling
        update twice (or with pre-existing statuses) would accumulate entries.
        """
        from api.models import Project

        existing_status = MagicMock()
        mock_instance = MagicMock(spec=Project)
        mock_instance.taskStatuses = [existing_status]  # 1 pre-existing status

        serializer = ProjectSerializer()
        validated_data = {
            "taskStatuses": [
                {"name": "New", "color": "FFFFFF", "order": 1}
            ]
        }
        MockStatus.return_value = MagicMock()

        with patch.object(mock_instance, "save"):
            serializer.update(mock_instance, validated_data)

        # Should be 1 (replaced), not 2 (appended to existing)
        self.assertEqual(len(mock_instance.taskStatuses), 1)

    def test_update_without_task_statuses_leaves_existing_unchanged(self):
        """If taskStatuses is absent from validated_data, leave the existing list alone."""
        from api.models import Project

        existing_status = MagicMock()
        mock_instance = MagicMock(spec=Project)
        mock_instance.taskStatuses = [existing_status]

        serializer = ProjectSerializer()
        validated_data = {"name": "Updated Name"}  # no taskStatuses key

        with patch.object(mock_instance, "save"):
            serializer.update(mock_instance, validated_data)

        self.assertEqual(len(mock_instance.taskStatuses), 1)
