from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from api.views import ProjectView
from api.models import Project, User


class ProjectViewTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email="test@example.com", username="testuser", password="password", role="MEMBER")
        self.admin = User.objects.create_user(email="admin@example.com", username="admin", password="password", role="ADMIN")
        self.member_project = Project.objects.create(name="Member Project", owner=self.admin, created_by=self.admin)
        self.admin_project = Project.objects.create(name="Admin Project", owner=self.admin, created_by=self.admin)
        self.jwt_token = self.get_jwt_token(self.user)

    def get_jwt_token(self, user):
        from rest_framework_simplejwt.tokens import AccessToken
        return str(AccessToken.for_user(user))

    def test_get_projects_member(self):
        request = self.factory.get('/projects/')
        request.user = self.user
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.jwt_token}'
        response = ProjectView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_projects_admin(self):
        request = self.factory.get('/projects/')
        request.user = self.admin
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.get_jwt_token(self.admin)}'
        response = ProjectView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_member(self):
        request_data = {"name": "New Project", "description": "Description of new project"}
        request = self.factory.post('/projects/', request_data, format='json')
        request.user = self.user
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.jwt_token}'
        response = ProjectView.as_view()(request)
        print(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
