from django import forms
from .models import Task
from users.models import Department  # Ensure you import the correct Department model
from django.forms.widgets import DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import Profile
from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import timezone
from django.utils import timezone
from .models import Task
from users.models import Department


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'due_datetime', 'department', 'user', 'is_department_task']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task description',
                'rows': 4
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'due_datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_department_task': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the logged-in user
        super().__init__(*args, **kwargs)

        # Restrict department and user options based on the logged-in user's role
        if self.user and not self.user.profile.is_manager:
            # Normal users see only their own department
            self.fields['department'].queryset = Department.objects.filter(id=self.user.profile.department.id)
            self.fields['is_department_task'].widget = forms.HiddenInput()  # Hide department-wide field for normal users
            self.fields['user'].widget = forms.HiddenInput()  # Hide user field for normal users
        elif self.user:
            # Managers see all departments
            self.fields['department'].queryset = Department.objects.all()

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if self.user and self.user.profile.is_manager:
            if user and user.profile.department != self.user.profile.department:
                raise forms.ValidationError("You can only assign tasks to users in your department.")
        return user

    def clean_due_datetime(self):
        due_datetime = self.cleaned_data.get('due_datetime')
        if due_datetime and due_datetime < timezone.now():
            raise forms.ValidationError("Due date and time cannot be in the past.")
        return due_datetime


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="None",
        label="Department",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    is_manager = forms.BooleanField(
        required=False,
        label="Is Department Manager?",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'department', 'is_manager']
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()  # Save the user instance

            # Create and associate the Profile
            Profile.objects.create(
                user=user,
                is_manager=self.cleaned_data['is_manager'],
                department=self.cleaned_data['department']
            )

        return user