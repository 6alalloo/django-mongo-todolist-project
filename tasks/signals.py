from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from tasks.models import Notification
from .models import Profile
from django.contrib.auth.models import User
import json

@receiver(pre_save, sender=Task)
def track_task_changes(sender, instance, **kwargs):
    if not instance.pk:
        # If the task is being created, do nothing
        return

    # Fetch the previous state of the task
    old_task = Task.objects.get(pk=instance.pk)
    changes = {}

    # Compare fields for changes
    for field in ['title', 'description', 'priority', 'status', 'due_datetime']:
        old_value = getattr(old_task, field)
        new_value = getattr(instance, field)
        if old_value != new_value:
            changes[field] = {'before': old_value, 'after': new_value}

    # If there are changes, create a notification
    if changes:
        Notification.objects.create(
            user=instance.user,
            title="Task Updated",
            message=f"The task '{instance.title}' has been updated.",
            task=instance,
            changes=changes
        )
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
