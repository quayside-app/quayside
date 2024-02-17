from django.test import SimpleTestCase
from django.urls import reverse, resolve
from api import views

class TestUrls(SimpleTestCase):

    def test_get_user_url(self):
        url = reverse('v1-get-user')
        self.assertEqual(url, '/api/v1/users')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.users.UserDetailAPIView)

    def test_create_user_url(self):
        url = reverse('v1-create-user')
        self.assertEqual(url, '/api/v1/users/create')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.createUser.CreateUserAPIView)

    def test_projects_list_url(self):
        url = reverse('v1-projects-list')
        self.assertEqual(url, '/api/v1/projects')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.projects.ProjectsAPIView)

    def test_project_details_url(self):
        url = reverse('v1-project-details', args=['your_project_id'])
        self.assertEqual(url, '/api/v1/project/your_project_id')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.project.ProjectAPIView)

    def test_tasks_list_url(self):
        url = reverse('v1-tasks-list')
        self.assertEqual(url, '/api/v1/tasks')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, views.tasks.TasksAPIView)
