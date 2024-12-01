from django.shortcuts import render, get_object_or_404, redirect
from tasks.models import Task
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from tasks.forms import TaskForm
from django.urls import reverse
from django.http import HttpResponseForbidden  
from django.db import connection
from django.http import JsonResponse


def home(request):
    return render(request, 'tasks/home.html')

@login_required
def tasks_view(request):
    user = request.user
    if user.profile.is_manager:
        # Managers see all tasks in their department
        tasks = Task.objects.filter(department=user.profile.department)
    else:
        # Regular users see only their own tasks
        tasks = Task.objects.filter(user=user)
    return render(request, 'tasks/tasks.html', {'tasks': tasks})


@login_required
def calendar_view(request):
    return render(request, 'tasks/calendar.html')

def signup_view(request):
    return render(request, 'tasks/signup.html')
@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})
@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)

            # Automatically assign the logged-in user for normal users
            if not request.user.profile.is_manager:
                task.user = request.user

            task.save()
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
            form.save()
            return redirect('tasks')  # Redirect to the task list page
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit'})
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user == task.user or (request.user.profile.is_manager and task.department == request.user.profile.department):
        task.delete()
        return redirect('tasks')
    else:
        return HttpResponseForbidden("You are not allowed to delete this task.")
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
