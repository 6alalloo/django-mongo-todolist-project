from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from tasks.models import Notification
from users.models import Profile
from django.contrib.auth.models import User
import json

@receiver(pre_save, sender=Task)
def track_task_changes(sender, instance, **kwargs):
    if not instance.pk:

        return


    old_task = Task.objects.get(pk=instance.pk)
    changes = {}


    for field in ['title', 'description', 'priority', 'status', 'due_datetime']:
        old_value = getattr(old_task, field)
        new_value = getattr(instance, field)
        if old_value != new_value:
            changes[field] = {'before': old_value, 'after': new_value}

    if changes:
        Notification.objects.create(
            user=instance.user,
            title="Task Updated",
            message=f"The task '{instance.title}' has been updated.",
            task=instance,
            changes=changes
        )
        


