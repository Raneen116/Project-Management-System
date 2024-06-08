from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views import ProjectView, TaskView, MilestoneView, AssignTasks

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("projects/", ProjectView.as_view(), name="projects"),
    path("tasks/", TaskView.as_view(), name="tasks"),
    path("milestones/", MilestoneView.as_view(), name="milestones"),
    path("assign-task/", AssignTasks.as_view(), name="assign_task"),
]
