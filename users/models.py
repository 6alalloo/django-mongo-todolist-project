from djongo import models
from django.contrib.auth.models import User  

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    is_manager = models.BooleanField(default=False)  # Role-based flag

    def __str__(self):
        return f"{self.user.username} - {'Manager' if self.is_manager else 'User'}"

