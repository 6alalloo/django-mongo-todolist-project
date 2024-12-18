from django.shortcuts import render, get_object_or_404, redirect
from tasks.models import Task
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from tasks.forms import TaskForm
from django.urls import reverse
from django.http import HttpResponseForbidden  
from django.db import connection
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db import models
from djongo import models
from tasks.models import Notification
from pymongo import MongoClient
from django.forms.models import model_to_dict
from .forms import SignupForm
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from datetime import timedelta

def home(request):
    return render(request, 'tasks/home.html')

@login_required
def tasks_view(request):
    user = request.user

    # Base queryset
    if user.profile.is_manager:
        tasks = Task.objects.filter(department=user.profile.department)
    else:
        tasks = Task.objects.filter(user=user)

    # Filters
    priority_filter = request.GET.get('priority')
    status_filter = request.GET.get('status')
    department_task_filter = request.GET.get('department_task')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('q')

    # Apply priority and status filters
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Apply search query
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # Fetch all tasks first before filtering on is_department_task
    tasks_list = list(tasks)  # Convert to a list to filter in Python

    # Filter for department-wide tasks in Python
    if department_task_filter is not None:
        if department_task_filter == "true":
            tasks_list = [task for task in tasks_list if task.is_department_task]
        elif department_task_filter == "false":
            tasks_list = [task for task in tasks_list if not task.is_department_task]

    # Apply sorting
    if sort_by:
        reverse = sort_by.startswith('-')
        sort_key = sort_by.lstrip('-')
        tasks_list = sorted(tasks_list, key=lambda x: getattr(x, sort_key, ''), reverse=reverse)

    # Add delete permissions and check for overdue tasks
    for task in tasks_list:
        task.can_delete = (
            task.user == user or 
            (user.profile.is_manager and task.department == user.profile.department)
        )
        # Check if the task is overdue
        task.is_overdue = task.due_datetime < timezone.now() and task.status != 'Completed'
        print(f"Task: {task.title}, Due: {task.due_datetime}, Overdue: {task.is_overdue}")

    return render(request, 'tasks/tasks.html', {
        'tasks': tasks_list,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'department_task_filter': department_task_filter,
        'sort_by': sort_by,
        'search_query': search_query
    })



@login_required
def calendar_view(request):
    return render(request, 'tasks/calendar.html')

def signup_view(request):
    return render(request, 'tasks/signup.html')
@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    can_delete = (
        task.user == request.user or 
        (request.user.profile.is_manager and task.department == request.user.profile.department)
    )
    return render(request, 'tasks/task_detail.html', {'task': task, 'can_delete': can_delete})

@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)

            # Automatically assign the logged-in user for normal users
            if not request.user.profile.is_manager:
                task.user = request.user

            task.created_by = request.user  # Log who created the task
            task.save()

            # Create notification for the assigned user
            if task.user:  # Ensure the task has an assigned user
                Notification.objects.create(
                    user=task.user,
                    title="New Task Assigned",
                    message=f"You have been assigned a new task: {task.title}.",
                    task_id=task.id,
                )

            return redirect('tasks')
    else:
        form = TaskForm(user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_edit_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()

            # Notify the user about task updates
            if updated_task.user:  # Ensure the task has an assigned user
                Notification.objects.create(
                    user=updated_task.user,
                    title="Task Updated",
                    message=f"The task '{updated_task.title}' has been updated.",
                    task=updated_task,
                )

            return redirect('tasks')  # Redirect to the task list page
    else:
        form = TaskForm(instance=task)
        can_delete = (
            task.user == request.user or 
            (request.user.profile.is_manager and task.department == request.user.profile.department)
        )
    return render(request, 'tasks/task_form.html', {'form': form, 'task': task, 'action': 'Edit', 'can_delete': can_delete})
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Permission logic:
    if task.is_department_task:
        # Only managers can delete department-wide tasks
        if not request.user.profile.is_manager or task.department != request.user.profile.department:
            return HttpResponseForbidden("You don't have permission to delete this department-wide task.")
    else:
        # Normal deletion logic for user-specific tasks
        if task.user != request.user and (
            not request.user.profile.is_manager or task.department != request.user.profile.department
        ):
            return HttpResponseForbidden("You don't have permission to delete this task.")

    # If all conditions are met, delete the task
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect('tasks')
class CustomLoginView(LoginView):
    template_name = 'tasks/login.html'

    def get_success_url(self):
        return reverse('tasks')
    
def calendar_data(request):
    tasks = Task.objects.filter(user=request.user) if not request.user.profile.is_manager else Task.objects.all()
    events = []

    for task in tasks:
        events.append({
            'title': task.title,
            'start': task.due_datetime.isoformat(),  # Format date for FullCalendar
            'url': f"/tasks/{task.id}/",  # Link to the task detail page
            'color': 'red' if task.priority == 'High' else 'blue',
        })

    return JsonResponse(events, safe=False)

def custom_logout(request):
    messages.success(request, "You have been logged out.")
    logout(request)
    return redirect('login')

@login_required
def notifications_view(request):
    # Fetch notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark notifications as read if user clicks "Mark All as Read"
    if request.method == 'POST' and 'mark_as_read' in request.POST:
        notifications.update(is_read=True)
        return redirect('notifications')

    return render(request, 'tasks/notifications.html', {'notifications': notifications})

@login_required
def notifications_unread_count(request):
    # Connect to MongoDB
    client = MongoClient("localhost", 27017)
    database = client['TDLdb']
    
    # Access the tasks_notification collection
    notifications_collection = database['tasks_notification']
    
    # Query for unread notifications
    unread_count = notifications_collection.count_documents({
        'user_id': request.user.id,
        'is_read': False
    })
    
    return JsonResponse({'unread_count': unread_count})

@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, id=pk, user=request.user)

    if not notification.is_read:
        notification.is_read = True
        notification.save()

# Ensure task exists before redirecting
    if notification.task:
        return redirect('task_detail', pk=notification.task.id)
    else:
        messages.error(request, "Task not found for this notification.")
        return redirect('notifications')
    
    

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks')  # Redirect to tasks
    else:
        form = SignupForm()
    return render(request, 'tasks/signup.html', {'form': form})    

@login_required
@require_POST
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Permission check
    if task.user != request.user and (
        not request.user.profile.is_manager or task.department != request.user.profile.department
    ):
        return HttpResponseForbidden("You don't have permission to complete this task.")

    # Update task status
    task.status = 'Completed'
    task.save()

    # Add a success message
    messages.success(request, f"Task '{task.title}' has been marked as completed.")

    return redirect('tasks')

@login_required
def dashboard_view(request):
    user = request.user

    # Base query: Managers see tasks for their department; users see their own tasks
    if user.profile.is_manager:
        tasks = Task.objects.filter(department=user.profile.department)
    else:
        tasks = Task.objects.filter(user=user)

    # Task counts by status
    task_counts = {
        'Pending': tasks.filter(status='Pending').count(),
        'In_Progress': tasks.filter(status='In Progress').count(),
        'Completed': tasks.filter(status='Completed').count(),
        'Overdue': tasks.filter(due_datetime__lt=timezone.now(), status__in=['Pending', 'In Progress']).count(),
    }

    # Overdue tasks
    overdue_tasks = tasks.filter(due_datetime__lt=timezone.now(), status__in=['Pending', 'In Progress']).count()

    # Tasks grouped by priority
    priority_counts = {
        'Low': tasks.filter(priority='Low').count(),
        'Medium': tasks.filter(priority='Medium').count(),
        'High': tasks.filter(priority='High').count(),
    }

    # Upcoming Deadlines: Tasks due within the next 7 days
    upcoming_deadlines = tasks.filter(
        due_datetime__gte=timezone.now(),  # Tasks due from now...
        due_datetime__lte=timezone.now() + timedelta(days=7),  # ... to 7 days in the future
        status__in=['Pending', 'In Progress']  # Only tasks that are not completed
    ).order_by('due_datetime')

    return render(request, 'tasks/dashboard.html', {
        'task_counts': task_counts,
        'overdue_tasks': overdue_tasks,
        'priority_counts': priority_counts,
        'upcoming_deadlines': upcoming_deadlines,
    })
