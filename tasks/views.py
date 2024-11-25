from django.shortcuts import render

def home(request):
    return render(request, 'tasks/home.html')

def tasks_view(request):
    # Example task data
    tasks = [
        {"title": "Finish Django Project", "priority": "High", "due_date": "2024-12-01"},
        {"title": "Team Meeting", "priority": "Medium", "due_date": "2024-12-05"},
        {"title": "Submit Report", "priority": "Low", "due_date": "2024-12-10"},
    ]
    return render(request, 'tasks/tasks.html', {"tasks": tasks})

def calendar_view(request):
    return render(request, 'tasks/calendar.html')

def signup_view(request):
    return render(request, 'tasks/signup.html')

