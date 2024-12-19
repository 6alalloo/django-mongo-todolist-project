from django.shortcuts import render, get_object_or_404, redirect
from tasks.models import Task
from users.models import Profile
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
from django.utils.timezone import now

def home(request):
    return render(request, 'tasks/home.html')

@login_required
def tasks_view(request):
    user = request.user
    if user.profile.is_manager:
        tasks = Task.objects.filter(department=user.profile.department)
    else:
        tasks = Task.objects.filter(user=user)

    priority_filter = request.GET.get('priority')
    status_filter = request.GET.get('status')
    department_task_filter = request.GET.get('department_task')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('q') or ""

    if priority_filter and priority_filter != "Filter by Priority":
        tasks = tasks.filter(priority=priority_filter)
    if status_filter and status_filter != "Filter by Status":
        tasks = tasks.filter(status=status_filter)

    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    if department_task_filter == "true":
        tasks = tasks.filter(is_department_task=True)
    elif department_task_filter == "false":
        tasks = tasks.filter(is_department_task=False)

    sort_mapping = {
        "due_date_asc": "due_datetime",
        "due_date_desc": "-due_datetime",
        "title_asc": "title",
        "title_desc": "-title",
        "priority_asc": "priority",
        "priority_desc": "-priority"
    }

    if sort_by in sort_mapping:
        sort_field = sort_mapping[sort_by]
    else:
        sort_field = "due_datetime"
        sort_by = ""

    tasks = tasks.order_by(sort_field)

    for task in tasks:
        task.can_delete = (
            task.user == user or 
            (user.profile.is_manager and task.department == user.profile.department)
        )
        task.is_overdue = task.due_datetime < timezone.now() and task.status != 'Completed'

    return render(request, 'tasks/tasks.html', {
        'tasks': tasks,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'department_task_filter': department_task_filter,
        'sort_by': sort_by,
        'search_query': search_query
    })

@login_required
def calendar_view(request):
    return render(request, 'tasks/calendar.html')

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
            if not request.user.profile.is_manager:
                task.user = request.user
            task.created_by = request.user
            task.save()
            if task.user:
                Notification.objects.create(
                    user=task.user,
                    title="New Task Assigned",
                    message=f"You have been assigned a new task: {task.title}.",
                    task_id=task.id,
                )
            return redirect('tasks')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

@login_required
def task_edit_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    can_delete = (
        task.user == request.user or
        (request.user.profile.is_manager and task.department == request.user.profile.department)
    )
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Task has been updated successfully.")
            return redirect('tasks')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(
        request,
        'tasks/task_form.html',
        {'form': form, 'task': task, 'action': 'Edit', 'can_delete': can_delete, 'title': 'Edit Task'}
    )

def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.is_department_task:
        if not request.user.profile.is_manager or task.department != request.user.profile.department:
            return HttpResponseForbidden("You don't have permission to delete this department-wide task.")
    else:
        if task.user != request.user and (
            not request.user.profile.is_manager or task.department != request.user.profile.department
        ):
            return HttpResponseForbidden("You don't have permission to delete this task.")
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect('tasks')

class CustomLoginView(LoginView):
    template_name = 'tasks/login.html'
    def get_success_url(self):
        return reverse('tasks')

@login_required
def calendar_data(request):
    user = request.user
    if user.profile.is_manager:
        tasks = Task.objects.filter(department=user.profile.department)
    else:
        tasks = Task.objects.filter(user=user)
    events = []
    for task in tasks:
        is_overdue = task.status != "Completed" and task.due_datetime < now()
        events.append({
            "title": task.title,
            "start": task.due_datetime.isoformat(),
            "url": f"/tasks/{task.id}/",
            "color": "red" if is_overdue else "blue",
            "priority": task.priority,
            "description": task.description or "No description provided.",
        })
    return JsonResponse(events, safe=False)

def custom_logout(request):
    messages.success(request, "You have been logged out.")
    logout(request)
    return redirect('login')

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    for notification in notifications:
        try:
            if notification.task:
                if "Task Assigned" in notification.title:
                    notification.title = f"New Task '{notification.task.title}' Assigned"
                elif "Task Updated" in notification.title:
                    notification.title = f"Task '{notification.task.title}' Updated"
                elif "Task Completed" in notification.title:
                    notification.title = f"Task '{notification.task.title}' Marked as Completed"
        except Task.DoesNotExist:
            notification.title = "Task no longer exists"
    if request.method == 'POST' and 'mark_as_read' in request.POST:
        notifications.update(is_read=True)
        return redirect('notifications')
    return render(request, 'tasks/notifications.html', {'notifications': notifications})

@login_required
def notifications_unread_count(request):
    client = MongoClient("localhost", 27017)
    database = client['TDLdb']
    notifications_collection = database['tasks_notification']
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
    if notification.task:
        return redirect('task_detail', pk=notification.task.id)
    else:
        messages.error(request, "Task not found for this notification.")
        return redirect('notifications')

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = SignupForm()
    return render(request, 'tasks/signup.html', {'form': form})

@login_required
@require_POST
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.user != request.user and (
        not request.user.profile.is_manager or task.department != request.user.profile.department
    ):
        return HttpResponseForbidden("You don't have permission to complete this task.")
    task.status = 'Completed'
    task.save()
    messages.success(request, f"Task '{task.title}' has been marked as completed.")
    return redirect('tasks')

@login_required
def dashboard_view(request):
    user = request.user
    if user.profile.is_manager:
        tasks = Task.objects.filter(department=user.profile.department)
    else:
        tasks = Task.objects.filter(user=user)
    task_counts = {
        'Pending': tasks.filter(status='Pending').count(),
        'In_Progress': tasks.filter(status='In Progress').count(),
        'Completed': tasks.filter(status='Completed').count(),
        'Overdue': tasks.filter(due_datetime__lt=timezone.now(), status__in=['Pending', 'In Progress']).count(),
    }
    overdue_tasks = tasks.filter(due_datetime__lt=timezone.now(), status__in=['Pending', 'In Progress']).count()
    priority_counts = {
        'Low': tasks.filter(priority='Low').count(),
        'Medium': tasks.filter(priority='Medium').count(),
        'High': tasks.filter(priority='High').count(),
    }
    upcoming_deadlines = tasks.filter(
        due_datetime__gte=timezone.now(),
        due_datetime__lte=timezone.now() + timedelta(days=7),
        status__in=['Pending', 'In Progress']
    ).order_by('due_datetime')
    return render(request, 'tasks/dashboard.html', {
        'task_counts': task_counts,
        'overdue_tasks': overdue_tasks,
        'priority_counts': priority_counts,
        'upcoming_deadlines': upcoming_deadlines,
    })
