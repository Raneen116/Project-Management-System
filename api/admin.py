from django.contrib import admin
from api.models import User, Project, Task, Milestone

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Milestone)
