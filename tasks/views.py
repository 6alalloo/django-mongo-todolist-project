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



def home(request):
    return render(request, 'tasks/home.html')

@login_required
def tasks_view(request):
    user = request.user

    # Fetch tasks based on user role
    if user.profile.is_manager:
        # Managers see all tasks in their department
        tasks = Task.objects.filter(department=user.profile.department)
    else:
        # Regular users see only their own tasks
        tasks = Task.objects.filter(user=user)
    
    # Add a flag to indicate if the user can delete the task
    for task in tasks:
        task.can_delete = (
            task.user == user or 
            (user.profile.is_manager and task.department == user.profile.department)
        )

    return render(request, 'tasks/tasks.html', {'tasks': tasks}) 


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
