from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Task, Milestone, Notification as NotificationModel
from api.tasks import send_email


@receiver(post_save, sender=Task)
def task_signal(sender, instance, created, update_fields, **kwargs):
    try:
        user = instance.assigned_to
        if (created and user) or user and update_fields:
            subject = "New task assigned."
            body = f"Hi {user.username}, A new task '{instance.name}' has been assigned to you by {instance.created_by.username}."
            NotificationModel.objects.create(user=user, subject=subject, body=body)
        elif user:
            subject = "Task updated."
            body = f"Hi {user.username}, task '{instance.name}' has been updated."
            NotificationModel.objects.create(user=user, subject=subject, body=body)
    except Exception as e:
        print(str(e))


@receiver(post_save, sender=Milestone)
def milestone_signal(sender, instance, created, **kwargs):
    try:
        user = instance.assigned_to
        subject = ""
        body = ""
        if created:
            subject = "New milestone assigned."
            body = f"Hi {user.username}, A new milestone '{instance.name}' has been assigned to you by {instance.created_by.username}."
        else:
            subject = "milestone updated."
            body = f"Hi {user.username}, milestone '{instance.name}' has been updated."
        NotificationModel.objects.create(user=user, subject=subject, body=body)
    except Exception as e:
        print(str(e))


@receiver(post_save, sender=NotificationModel)
def notification_signal(sender, instance, created, **kwargs):
    try:
        if created:
            send_email.delay(
                subject=instance.subject,
                message=instance.body,
                recipient_list=[instance.user.email],
            )
    except Exception as e:
        print(str(e))
