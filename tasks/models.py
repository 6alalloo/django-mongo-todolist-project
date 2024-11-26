from djongo import models


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

    user = models.ForeignKey(
    'auth.User',  # Link to Django's built-in User model
    on_delete=models.SET_NULL,  # Set user to NULL when the user is deleted
    null=True,  # Allow NULL values
    blank=True  # Allow this field to be empty in forms
    )
    
    

    def __str__(self):
        return self.title
