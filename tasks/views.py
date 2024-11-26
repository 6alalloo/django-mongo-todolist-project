from django.shortcuts import render
from tasks.models import Task
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'tasks/home.html')

@login_required
def tasks_view(request):
    
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/tasks.html', {"tasks": tasks})

def calendar_view(request):
    return render(request, 'tasks/calendar.html')

def signup_view(request):
    return render(request, 'tasks/signup.html')

