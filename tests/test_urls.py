from django.test import SimpleTestCase
from django.urls import reverse, resolve
from api import views as api_views
from app import views as app_views
from quayside import views as quayside_views
import re


class TestAPIUrls(SimpleTestCase):
    def test_get_user_url(self):
        url = reverse("v1-get-user")
        self.assertEqual(url, "/api/v1/users/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, api_views.users.UsersAPIView)

    def test_projects_list_url(self):
        url = reverse("v1-projects-list")
        self.assertEqual(url, "/api/v1/projects/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, api_views.projects.ProjectsAPIView)

    def test_tasks_list_url(self):
        url = reverse("v1-tasks-list")
        self.assertEqual(url, "/api/v1/tasks/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, api_views.tasks.TasksAPIView)

    def test_generated_tasks_url(self):
        url = reverse("v1-generated-tasks")
        self.assertEqual(url, "/api/v1/generatedTasks/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, api_views.generatedTasks.GeneratedTasksAPIView)

    def test_kanban_url(self):
        url = reverse("v1-kanban-board")
        self.assertEqual(url, "/api/v1/kanban/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, api_views.kanban.KanbanAPIView)

    def test_statuses_url(self):
        url = reverse("v1-status-list")
        self.assertEqual(url, "/api/v1/statuses/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, api_views.statuses.StatusesAPIView)

    # ADD API URL TESTS HERE...


class TestAppUrls(SimpleTestCase):
    """
    Copy and paste the stuff inside the parenthases of the path function in app.views.py to add a test case.
    Just change views. to app_views in the second column.
    """
    url_data = [
        ("/create-project/", app_views.createProjectView, "create-project-view"),
        ("/project/<str:projectID>/graph/", app_views.projectGraphView, "project-graph-view"),
        ("/project/<str:projectID>/kanban/", app_views.projectKanbanView, "project-kanban-view"),
        ("/project/<str:projectID>/", app_views.editProjectView, "task-detail-view"),
        ("/project/<str:projectID>/graph/task/<str:taskID>/", app_views.taskView, "task-detail-view"),
        ("/project/<str:projectID>/graph/create-task/<str:parentTaskID>/", app_views.createTaskView, "create-task-view"),
        ("/project/<str:projectID>/graph/create-task/", app_views.createTaskView, "create-task-view"),
        ("/login/", app_views.userLogin, "login-view"),
        ("/logout/", app_views.userLogout, "userLogout-view"),
        ("/welcome/", app_views.logout, "logout-view"),
        ("/invite/", app_views.inviteView, "invite-view"),
        ("/tutorial/", app_views.tutorialView, "tutorial-view"),
        ("/marketplace/", app_views.marketplaceView, "marketplace-view"),
        ("/feedback/", app_views.feedbackView, "feedback-view"),
        ("/auth/<str:provider>/", app_views.requestAuth, "authorize"),
        ("/callback/", app_views.Callback.as_view(), "callback"),
        ("/redirect/", app_views.redirectOffSite, "offsite-redirect"),
    ]

    def test_urls(self):
        # reverse() needs to know what values to fill in the dynamic bits with.
        # I couldn't find a simple way to do this, therefore we have a regular expression and some other logic.

        for url, view_func, url_name in self.url_data:
            # Finds 'x' in '/a/<b:x>/c/'
            dynamic_parts = re.findall(r'<[^:]*:\s*([^>]*)>', url) 
            kwargs = {part: "test_" + part for part in dynamic_parts}
            
            with self.subTest(url=url):
                # Replace dynamic parts with test values
                for part, test_value in kwargs.items():
                    url = url.replace(f"<str:{part}>", test_value)
                

                generated_url = reverse(url_name, kwargs=kwargs)
                self.assertEqual(generated_url, url)
                resolver = resolve(url)
                self.assertEqual(resolver.func, view_func)



class TestRootUrls(SimpleTestCase):
    def test_index_url(self):
        url = reverse("index")
        self.assertEqual(url, "/")
        resolver = resolve(url)
        self.assertEqual(resolver.func, quayside_views.index)

    # ADD QUAYSIDE URL TESTS HERE...