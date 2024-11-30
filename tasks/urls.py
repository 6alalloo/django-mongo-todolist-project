from django.urls import path
from . import views
from .views import CustomLoginView, task_delete_view
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.shortcuts import redirect

def custom_logout(request):
    messages.success(request, "You have been logged out.")
    return redirect('login')

urlpatterns = [
    path('',views.home, name='home'),
    path('tasks', views.tasks_view, name='tasks'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('signup/', views.signup_view, name='signup'),
    path('tasks/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_edit_view, name='task_edit'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('tasks/<int:pk>/delete/', task_delete_view, name='task_delete'),
]




