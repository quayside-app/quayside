from django.test import SimpleTestCase
from django.urls import reverse, resolve
from api import views


class TestUrls(SimpleTestCase):

    def test_get_user_url(self):
        url = reverse("v1-get-user")
        self.assertEqual(url, "/api/v1/users")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.users.UserDetailAPIView)

    def test_projects_list_url(self):
        url = reverse("v1-projects-list")
        self.assertEqual(url, "/api/v1/projects")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.projects.ProjectsAPIView)

    def test_tasks_list_url(self):
        url = reverse("v1-tasks-list")
        self.assertEqual(url, "/api/v1/tasks")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.tasks.TasksAPIView)
