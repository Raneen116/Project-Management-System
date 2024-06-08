from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        if not username:
            raise ValueError(_("The username field must be set"))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if extra_fields.get("role") != "ADMIN":
            raise ValueError(_("Superuser must have role=admin."))

        return self.create_user(email, username, password, **extra_fields)


class UserRoles(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    MANAGER = "MANAGER", _("Manager")
    MEMBER = "MEMBER", _("Member")


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=10, choices=UserRoles.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        User, related_name="owned_projects", on_delete=models.CASCADE
    )
    members = models.ManyToManyField(User, related_name="assigned_projects", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_projects"
    )

    def __str__(self):
        return self.name


class Status(models.TextChoices):
    NOT_YET_STARTED = "NOT_YET_STARTED", _("not yet started")
    IN_PROGRESS = "IN_PROGRESS", _("in progress")
    COMPLETED = "COMPLETED", _("completed")
    ON_HOLD = "ON_HOLD", _("on hold")


class Task(models.Model):

    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.TextField(choices=Status.choices, default=Status.NOT_YET_STARTED)
    due_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )

    def __str__(self):
        return self.name


class Milestone(models.Model):
    project = models.ForeignKey(
        Project, related_name="milestones", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    is_achieved = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(
        User,
        related_name="assigned_milestones",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_milestones"
    )

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ForeignKey(
        User, related_name="notifications", on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}-{self.subject}"
