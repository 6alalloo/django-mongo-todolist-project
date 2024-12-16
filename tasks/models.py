from djongo import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=255)  # Task title
    description = models.TextField(blank=True, null=True)  # Optional description
    priority = models.CharField(
        max_length=10,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
        default='Medium'
    )  # Task priority
    due_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Pending'
    )  # Task status
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updated on save
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey('users.Department', on_delete=models.CASCADE, null=True, blank=True)
    is_department_task = models.BooleanField(default=False)
    user = models.ForeignKey(
    'auth.User',  # Link to Django's built-in User model
    on_delete=models.SET_NULL,  # Set user to NULL when the user is deleted
    null=True,  # Allow NULL values
    blank=True
    )
    is_department_task = models.BooleanField(default=False)# Allow this field to be empty in forms
    created_by = models.ForeignKey(
    'auth.User',
    on_delete=models.CASCADE,
    related_name='created_tasks',
    null=True,
    blank=True,
)
    
    def __str__(self):
        return self.title
    def task_type(self):
        return "Department-Wide" if self.is_department_task else "User-Specific"
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)  # This line
    

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
    
class Profile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    is_manager = models.BooleanField(default=False)
    related_name="profile"

    def __str__(self):
        return f"{self.user.username}'s Profile"