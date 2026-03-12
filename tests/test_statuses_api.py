from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase
from rest_framework import status as http_status
from bson import ObjectId

from api.views.v1.statuses import StatusesAPIView


def make_project(statuses):
    return {
        "id": str(ObjectId()),
        "name": "Test Project",
        "taskStatuses": statuses,
    }


class TestCreateStatus(SimpleTestCase):

    @patch("api.views.v1.statuses.ProjectSerializer")
    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_create_sets_max_plus_one_order(self, mock_get, MockSerializer):
        project = make_project([
            {"id": str(ObjectId()), "name": "Todo", "color": "323232", "order": 1},
            {"id": str(ObjectId()), "name": "Done", "color": "01796E", "order": 2},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        _, code = StatusesAPIView.createStatus(
            {"projectID": project["id"], "name": "In Review", "color": "4A90E2"},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_201_CREATED)
        new_status = project["taskStatuses"][-1]
        self.assertEqual(new_status["order"], 3)
        self.assertEqual(new_status["name"], "In Review")

    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_create_rejects_duplicate_name_case_insensitive(self, mock_get):
        project = make_project([
            {"id": str(ObjectId()), "name": "Todo", "color": "323232", "order": 1},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)

        _, code = StatusesAPIView.createStatus(
            {"projectID": project["id"], "name": "todo", "color": "4A90E2"},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_409_CONFLICT)

    @patch("api.views.v1.statuses.ProjectSerializer")
    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_create_appends_exactly_one_status(self, mock_get, MockSerializer):
        """Regression: old code appended inside the for loop, creating duplicates."""
        project = make_project([
            {"id": str(ObjectId()), "name": "Todo", "color": "323232", "order": 1},
            {"id": str(ObjectId()), "name": "Done", "color": "01796E", "order": 2},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        StatusesAPIView.createStatus(
            {"projectID": project["id"], "name": "New Column", "color": "FFFFFF"},
            "token",
        )

        self.assertEqual(len(project["taskStatuses"]), 3)

    @patch("api.views.v1.statuses.ProjectSerializer")
    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_create_works_when_task_statuses_is_empty(self, mock_get, MockSerializer):
        """Regression: old guard blocked creation when taskStatuses list was empty."""
        project = make_project([])  # no existing statuses
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        _, code = StatusesAPIView.createStatus(
            {"projectID": project["id"], "name": "First Column", "color": "4A90E2"},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_201_CREATED)
        self.assertEqual(len(project["taskStatuses"]), 1)
        self.assertEqual(project["taskStatuses"][0]["order"], 1)

    @patch("api.views.v1.statuses.ProjectSerializer")
    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_create_defaults_color_when_omitted(self, mock_get, MockSerializer):
        project = make_project([
            {"id": str(ObjectId()), "name": "Todo", "color": "323232", "order": 1},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        StatusesAPIView.createStatus(
            {"projectID": project["id"], "name": "Backlog"},
            "token",
        )

        new_status = project["taskStatuses"][-1]
        self.assertIn("color", new_status)
        self.assertTrue(len(new_status["color"]) == 6)


class TestUpdateStatus(SimpleTestCase):

    @patch("api.views.v1.statuses.ProjectSerializer")
    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_update_name_only_leaves_color_unchanged(self, mock_get, MockSerializer):
        status_id = str(ObjectId())
        project = make_project([
            {"id": status_id, "name": "Todo", "color": "323232", "order": 1},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        _, code = StatusesAPIView.updateStatus(
            {"projectID": project["id"], "id": status_id, "name": "Backlog"},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_200_OK)
        stat = project["taskStatuses"][0]
        self.assertEqual(stat["name"], "Backlog")
        self.assertEqual(stat["color"], "323232")

    @patch("api.views.v1.statuses.ProjectSerializer")
    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_update_color_only_leaves_name_unchanged(self, mock_get, MockSerializer):
        status_id = str(ObjectId())
        project = make_project([
            {"id": status_id, "name": "Todo", "color": "323232", "order": 1},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        _, code = StatusesAPIView.updateStatus(
            {"projectID": project["id"], "id": status_id, "color": "FF0000"},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_200_OK)
        stat = project["taskStatuses"][0]
        self.assertEqual(stat["color"], "FF0000")
        self.assertEqual(stat["name"], "Todo")

    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_update_unknown_id_returns_404(self, mock_get):
        project = make_project([
            {"id": str(ObjectId()), "name": "Todo", "color": "323232", "order": 1},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)

        _, code = StatusesAPIView.updateStatus(
            {"projectID": project["id"], "id": str(ObjectId()), "name": "X"},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_404_NOT_FOUND)


class TestDeleteStatus(SimpleTestCase):

    @patch("api.views.v1.statuses.ProjectSerializer")
    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_delete_recompacts_orders_to_contiguous_sequence(self, mock_get, MockSerializer):
        id1, id2, id3 = str(ObjectId()), str(ObjectId()), str(ObjectId())
        project = make_project([
            {"id": id1, "name": "Todo", "color": "323232", "order": 1},
            {"id": id2, "name": "In-Progress", "color": "EFA610", "order": 2},
            {"id": id3, "name": "Done", "color": "01796E", "order": 3},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        _, code = StatusesAPIView.deleteStatus(
            {"projectID": project["id"], "id": id2},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_200_OK)
        self.assertEqual(len(project["taskStatuses"]), 2)
        orders = sorted(s["order"] for s in project["taskStatuses"])
        self.assertEqual(orders, [1, 2])

    @patch("api.views.v1.statuses.ProjectsAPIView.getProjects")
    def test_delete_unknown_id_returns_404(self, mock_get):
        project = make_project([
            {"id": str(ObjectId()), "name": "Todo", "color": "323232", "order": 1},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)

        _, code = StatusesAPIView.deleteStatus(
            {"projectID": project["id"], "id": str(ObjectId())},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_404_NOT_FOUND)


class TestReorderStatuses(SimpleTestCase):

    @patch("api.views.v1.statusesReorder.ProjectSerializer")
    @patch("api.views.v1.statusesReorder.ProjectsAPIView.getProjects")
    def test_reorder_updates_order_fields(self, mock_get, MockSerializer):
        from api.views.v1.statusesReorder import StatusesReorderAPIView
        id1, id2, id3 = str(ObjectId()), str(ObjectId()), str(ObjectId())
        project = make_project([
            {"id": id1, "name": "Todo", "color": "323232", "order": 1},
            {"id": id2, "name": "In-Progress", "color": "EFA610", "order": 2},
            {"id": id3, "name": "Done", "color": "01796E", "order": 3},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)
        mock_ser = MagicMock()
        mock_ser.is_valid.return_value = True
        MockSerializer.return_value = mock_ser

        _, code = StatusesReorderAPIView.reorderStatuses(
            {"projectID": project["id"], "orderedIds": [id3, id1, id2]},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_200_OK)
        id_to_order = {s["id"]: s["order"] for s in project["taskStatuses"]}
        self.assertEqual(id_to_order[id3], 1)
        self.assertEqual(id_to_order[id1], 2)
        self.assertEqual(id_to_order[id2], 3)

    @patch("api.views.v1.statusesReorder.ProjectsAPIView.getProjects")
    def test_reorder_mismatch_returns_400(self, mock_get):
        from api.views.v1.statusesReorder import StatusesReorderAPIView
        id1, id2 = str(ObjectId()), str(ObjectId())
        project = make_project([
            {"id": id1, "name": "Todo", "color": "323232", "order": 1},
            {"id": id2, "name": "Done", "color": "01796E", "order": 2},
        ])
        mock_get.return_value = ([project], http_status.HTTP_200_OK)

        _, code = StatusesReorderAPIView.reorderStatuses(
            {"projectID": project["id"], "orderedIds": [id1, str(ObjectId())]},
            "token",
        )

        self.assertEqual(code, http_status.HTTP_400_BAD_REQUEST)
