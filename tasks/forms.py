from django import forms
from .models import Task
from users.models import Department  # Ensure you import the correct Department model
from django.forms.widgets import DateTimeInput


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'due_datetime', 'department', 'user', 'is_department_task']
        widgets = {
            'due_datetime': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the logged-in user
        super().__init__(*args, **kwargs)

        if self.user and not self.user.profile.is_manager:
            # Normal users see only their own department
            self.fields['department'].queryset = Department.objects.filter(id=self.user.profile.department.id)
            self.fields['is_department_task'].widget = forms.HiddenInput()  # Hide department-wide field for normal users
        elif self.user:
            # Managers see all departments
            self.fields['department'].queryset = Department.objects.all()

        # Hide the 'user' field for normal users
        if self.user and not self.user.profile.is_manager:
            self.fields['user'].widget = forms.HiddenInput()

        # Only show the 'is_department_task' field to managers
        if self.user and not self.user.profile.is_manager:
            self.fields['is_department_task'].widget = forms.HiddenInput()

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if self.user and self.user.profile.is_manager:
            if user and user.profile.department != self.user.profile.department:
                raise forms.ValidationError("You can only assign tasks to users in your department.")
        return user
