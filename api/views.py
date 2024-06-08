from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from api.utils import custom_response
from api.models import Project, Task, Milestone, UserRoles, User
from api.serializers import ProjectSerializer, TaskSerializer, MilestoneSerializer
from api.api_permission import permit_if_role_in
from django.core.cache import cache


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @permit_if_role_in([UserRoles.MEMBER])
    def get(self, request, *args, **kwargs):
        try:
            if cache.get("projects"):
                queryset = cache.get("projects")
            else:
                queryset = (
                    Project.objects.select_related("owner", "created_by")
                    .prefetch_related("members")
                    .all()
                )
                cache.set("projects", queryset, timeout=None)
            serializer = ProjectSerializer(
                queryset,
                many=True,
                fields=["id", "name", "description", "owner", "member_details"],
            )
            return custom_response(
                data=serializer.data,
                message="Showing all the Projects.",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN])
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            data["owner"] = request.user
            data["created_by"] = request.user
            serializer = ProjectSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                cache.delete("projects")
                return custom_response(
                    message="Project created successfully.",
                    status=status.HTTP_201_CREATED,
                )
            else:
                return custom_response(
                    message=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN, UserRoles.MANAGER])
    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            project_id = data.get("id")
            if project_id:
                instance = (
                    Project.objects.select_related("owner", "created_by")
                    .prefetch_related("members")
                    .get(pk=project_id)
                )
                serializer = ProjectSerializer(
                    instance=instance, data=data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return custom_response(
                        message="Project updated successfully.",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return custom_response(
                        message=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return custom_response(
                message="id is required.", status=status.HTTP_400_BAD_REQUEST
            )
        except Project.DoesNotExist:
            return custom_response(
                message="No project with given id.", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN])
    def delete(self, request, *args, **kwargs):
        try:
            project_id = request.query_params.get("id")
            project = Project.objects.get(pk=project_id)
            project.delete()
            return custom_response(
                message="Project deleted successfully.",
                status=status.HTTP_204_NO_CONTENT,
            )
        except Project.DoesNotExist:
            return custom_response(
                message="No project with the given id.",
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return custom_response(str(e), status=status.HTTP_400_BAD_REQUEST)


class TaskView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @permit_if_role_in([UserRoles.MEMBER])
    def get(self, request, *args, **kwargs):
        try:
            if cache.get("tasks"):
                queryset = cache.get("tasks")
            else:
                queryset = Task.objects.select_related(
                    "project", "assigned_to", "created_by"
                ).all()
            serializer = TaskSerializer(
                queryset,
                many=True,
                fields=[
                    "id",
                    "project_name",
                    "name",
                    "description",
                    "assigned_user",
                    "status",
                ],
            )
            return custom_response(
                data=serializer.data,
                message="Showing all the Tasks.",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN])
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            data["created_by"] = request.user
            serializer = TaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                cache.delete("tasks")
                return custom_response(
                    message="Task created successfully.",
                    status=status.HTTP_201_CREATED,
                )
            else:
                return custom_response(
                    message=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN, UserRoles.MANAGER])
    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            task_id = data.get("id")
            if task_id:
                instance = Task.objects.select_related(
                    "project", "assigned_to", "created_by"
                ).get(pk=task_id)
                serializer = TaskSerializer(instance=instance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return custom_response(
                        message="Task updated successfully.",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return custom_response(
                        message=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return custom_response(
                message="id is required.", status=status.HTTP_400_BAD_REQUEST
            )
        except Task.DoesNotExist:
            return custom_response(
                message="No task with given id.", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN])
    def delete(self, request, *args, **kwargs):
        try:
            task_id = request.query_params.get("id")
            task = Task.objects.get(pk=task_id)
            task.delete()
            return custom_response(
                message="Task deleted successfully.",
                status=status.HTTP_204_NO_CONTENT,
            )
        except Task.DoesNotExist:
            return custom_response(
                message="No task with the given id.",
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return custom_response(str(e), status=status.HTTP_400_BAD_REQUEST)


class MilestoneView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @permit_if_role_in([UserRoles.MEMBER])
    def get(self, request, *args, **kwargs):
        try:
            queryset = Milestone.objects.select_related(
                "project", "assigned_to", "created_by"
            ).all()
            serializer = MilestoneSerializer(
                queryset,
                many=True,
                fields=[
                    "id",
                    "name",
                    "description",
                    "due_date",
                    "project_name",
                    "is_achieved",
                ],
            )
            return custom_response(
                data=serializer.data,
                message="Showing all the milestones.",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN])
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            data["created_by"] = request.user
            serializer = MilestoneSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return custom_response(
                    message="Milestone created successfully.",
                    status=status.HTTP_201_CREATED,
                )
            else:
                return custom_response(
                    message=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN, UserRoles.MANAGER])
    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            task_id = data.get("id")
            if task_id:
                instance = Milestone.objects.select_related(
                    "project", "assigned_to", "created_by"
                ).get(pk=task_id)
                serializer = MilestoneSerializer(
                    instance=instance, data=data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return custom_response(
                        message="Milestone updated successfully.",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return custom_response(
                        message=serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return custom_response(
                message="id is required.", status=status.HTTP_400_BAD_REQUEST
            )
        except Milestone.DoesNotExist:
            return custom_response(
                message="No milestone with given id.", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)

    @permit_if_role_in([UserRoles.ADMIN])
    def delete(self, request, *args, **kwargs):
        try:
            milestone_id = request.query_params.get("id")
            milestone = Milestone.objects.get(pk=milestone_id)
            milestone.delete()
            return custom_response(
                message="milestone deleted successfully.",
                status=status.HTTP_204_NO_CONTENT,
            )
        except Milestone.DoesNotExist:
            return custom_response(
                message="No milestone with the given id.",
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return custom_response(str(e), status=status.HTTP_400_BAD_REQUEST)


class AssignTasks(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @permit_if_role_in([UserRoles.ADMIN, UserRoles.MANAGER])
    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            task_id = data.get("task")
            if task_id:
                instance = Task.objects.select_related(
                    "project", "assigned_to", "created_by"
                ).get(pk=task_id)
                assigned_projets = User.objects.get(
                    pk=data.get("assigned_to")
                ).assigned_projects.all()
                if instance.project in assigned_projets:
                    instance.assigned_to_id = data.get("assigned_to")
                    instance.save(update_fields=["assigned_to"])
                    return custom_response(
                        message="Task assigned successfully.", status=status.HTTP_200_OK
                    )
                else:
                    return custom_response(
                        message="The user is not assigned to the project that belongs this task.",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return custom_response(
                message="id is required.", status=status.HTTP_400_BAD_REQUEST
            )
        except Task.DoesNotExist:
            return custom_response(
                message="No task with given id.", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return custom_response(message=str(e), status=status.HTTP_400_BAD_REQUEST)
