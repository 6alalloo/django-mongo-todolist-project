from django.utils import timezone
from .models import Task, Notification

def check_deadlines():
    now = timezone.now()
    one_hour_later = now + timezone.timedelta(hours=1)
    one_day_later = now + timezone.timedelta(hours=25)

    for task in Task.objects.filter(due_datetime__lte=one_day_later, due_datetime__gt=now):
        Notification.objects.get_or_create(
            user=task.user,
            title="Task Due Soon",
            message=f"Your task '{task.title}' is due in 1 day.",
            task=task
        )
    for task in Task.objects.filter(due_datetime__lte=one_hour_later, due_datetime__gt=now):
        Notification.objects.get_or_create(
            user=task.user,
            title="Task Due Very Soon",
            message=f"Your task '{task.title}' is due in 1 hour.",
            task=task
        )