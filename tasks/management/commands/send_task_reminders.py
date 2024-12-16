from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from tasks.models import Task, Notification

class Command(BaseCommand):
    help = "Send reminders for tasks nearing their deadlines."

    def handle(self, *args, **kwargs):
        # Tasks due in 1 hour
        one_hour = now() + timedelta(hours=1)
        tasks_due_soon = Task.objects.filter(due_datetime__lte=one_hour, due_datetime__gte=now())

        for task in tasks_due_soon:
            if task.user:
                Notification.objects.get_or_create(
                    user=task.user,
                    title="Task Due Soon",
                    message=f"The task '{task.title}' is due in 1 hour.",
                    task=task,
                )

        # Tasks due in 1 day
        one_day = now() + timedelta(days=1)
        tasks_due_tomorrow = Task.objects.filter(due_datetime__lte=one_day, due_datetime__gte=now() + timedelta(hours=1))

        for task in tasks_due_tomorrow:
            if task.user:
                Notification.objects.get_or_create(
                    user=task.user,
                    title="Task Due Tomorrow",
                    message=f"The task '{task.title}' is due in 1 day.",
                    task=task,
                )

        self.stdout.write("Task reminders sent successfully!")