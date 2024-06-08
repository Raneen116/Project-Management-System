from django.test import TestCase
from django.core.exceptions import ValidationError
from api.models import User, Project, Task


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="pass", email="user1@example.com", role="ADMIN"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass", email="user2@example.com", role="MEMBER"
        )

    def test_create_project(self):
        project = Project.objects.create(
            name="Test Project",
            description="A test project description",
            owner=self.user1,
            created_by=self.user1,
        )
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.description, "A test project description")
        self.assertEqual(project.owner, self.user1)
        self.assertEqual(project.created_by, self.user1)

    def test_project_string_representation(self):
        project = Project.objects.create(
            name="Test Project", owner=self.user1, created_by=self.user1
        )
        self.assertEqual(str(project), project.name)

    def test_unique_project_name(self):
        Project.objects.create(
            name="Unique Project", owner=self.user1, created_by=self.user1
        )
        with self.assertRaises(Exception):
            Project.objects.create(
                name="Unique Project", owner=self.user2, created_by=self.user2
            )

    def test_project_members(self):
        project = Project.objects.create(
            name="Project with Members", owner=self.user1, created_by=self.user1
        )
        project.members.add(self.user1, self.user2)
        self.assertIn(self.user1, project.members.all())
        self.assertIn(self.user2, project.members.all())

    def test_blank_description(self):
        project = Project.objects.create(
            name="No Description Project", owner=self.user1, created_by=self.user1
        )
        self.assertEqual(project.description, None)

    def test_nullable_description(self):
        project = Project.objects.create(
            name="Nullable Description Project",
            owner=self.user1,
            created_by=self.user1,
            description=None,
        )
        self.assertIsNone(project.description)

    def test_created_by_foreign_key_constraint(self):
        with self.assertRaises(Exception):
            Project.objects.create(
                name="Invalid Created By", owner=self.user1, created_by=None
            )


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="password",
            role="ADMIN",
        )
        self.project = Project.objects.create(
            name="Test Project",
            description="Description of test project",
            owner=self.user,
            created_by=self.user,
        )
        self.valid_task_data = {
            "project": self.project,
            "name": "Test Task",
            "description": "Description of test task",
            "assigned_to": self.user,
            "status": "IN_PROGRESS",
            "due_date": "2024-12-31",
            "created_by": self.user,
        }

    def test_create_task(self):
        task = Task.objects.create(**self.valid_task_data)
        self.assertEqual(task.name, self.valid_task_data["name"])
        self.assertEqual(task.description, self.valid_task_data["description"])
        self.assertEqual(task.assigned_to, self.valid_task_data["assigned_to"])
        self.assertEqual(task.status, self.valid_task_data["status"])
        self.assertEqual(task.due_date, self.valid_task_data["due_date"])
        self.assertEqual(task.created_by, self.valid_task_data["created_by"])


class UserModelTest(TestCase):
    def setUp(self):
        self.valid_user_data = {
            "email": "user@example.com",
            "username": "user1",
            "password": "pass1234",
            "role": "ADMIN",
        }

    def test_create_user_with_valid_data(self):
        user = User.objects.create_user(**self.valid_user_data)
        self.assertEqual(user.email, self.valid_user_data["email"])
        self.assertEqual(user.username, self.valid_user_data["username"])
        self.assertEqual(user.role, self.valid_user_data["role"])
        self.assertTrue(user.check_password(self.valid_user_data["password"]))

    def test_user_string_representation(self):
        user = User.objects.create_user(**self.valid_user_data)
        self.assertEqual(str(user), user.username)

    def test_invalid_role_choice(self):
        invalid_user_data = self.valid_user_data.copy()
        invalid_user_data["role"] = "invalid_role"
        with self.assertRaises(ValidationError):
            user = User(**invalid_user_data)
            user.full_clean()
