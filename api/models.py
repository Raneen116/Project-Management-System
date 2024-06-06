from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("role") != "ADMIN":
            raise ValueError("Sper admin must have role='ADMIN'")

        return self.create_user(email, password, **extra_fields)


class UserRoles(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    MANAGER = "MANAGER", _("Manager")
    MEMBER = "MEMBER", _("Member")


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRoles.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        User, related_name="owned_projects", on_delete=models.CASCADE
    )
    members = models.ManyToManyField(User, related_name='assigned_projects', null=True, blank=True)

    def __str__(self):
        return self.name


class Status(models.TextChoices):
    NOT_YET_STARTED = "NOT_YET_STARTED", _("not yet started")
    IN_PROGRESS = "IN_PROGRESS", _("in progress")
    COMPLETED = "COMPLETED", _("completed")
    ON_HOLD = "ON_HOLD", _("on hold")


class Task(models.Model):

    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
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

    def __str__(self):
        return self.name


class Milestone(models.Model):
    project = models.ForeignKey(
        Project, related_name="milestones", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    is_achieved = models.BooleanField(default=False)

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
