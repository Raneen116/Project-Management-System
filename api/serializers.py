from rest_framework import serializers
from api.models import User, Project, Task, Milestone


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class ProjectSerializer(DynamicFieldsModelSerializer):
    member_details = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = "__all__"

    def get_member_details(self, obj):
        queryset = obj.members.all()
        serializer = UserSerializer(
            queryset, many=True, fields=["id", "username", "email"]
        )
        return serializer.data


class TaskSerializer(DynamicFieldsModelSerializer):
    project_name = serializers.SerializerMethodField()
    assigned_user = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = "__all__"

    def get_project_name(self, obj):
        return obj.project.name

    def get_assigned_user(self, obj):
        return obj.assigned_to.username

    def validate(self, attrs):
        members = attrs.get("project").members.all()
        if attrs.get("assigned_to"):
            if attrs.get("assigned_to") not in members:
                raise serializers.ValidationError(
                    "This user not belong to the parent project."
                )
        return attrs


class MilestoneSerializer(DynamicFieldsModelSerializer):
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Milestone
        fields = "__all__"

    def get_project_name(self, obj):
        return obj.project.name
