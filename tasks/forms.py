from django import forms
from .models import Task
from users.models import Department  # Ensure you import the correct Department model
from django.forms.widgets import DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), 
        required=False, 
        empty_label="None", 
        label="Department"
    )
    is_manager = forms.BooleanField(required=False, label="Is Department Manager?")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'department', 'is_manager']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Custom logic to link department and manager status
            profile = user.profile  # Assuming a OneToOne field to Profile
            profile.department = self.cleaned_data['department']
            profile.is_manager = self.cleaned_data['is_manager']
            profile.save()
        return user