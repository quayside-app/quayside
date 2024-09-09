from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.urls import reverse
from api.decorators import apiKeyRequired
from apiProjects import KanbanAPIView
from rest_framework import status

# Helpful link: https://stackoverflow.com/questions/11885211/how-to-write-a-unit-test-for-a-django-view

class TestKanban(TestCase):
    def test_call_view_deny_anonymous(self):
        url = reverse("v1-kanban-board")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
