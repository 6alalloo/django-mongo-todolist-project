from djongo import models
from django.contrib.auth.models import User  

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL
    )
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

