from django.urls import path
from . import views
from .views import CustomLoginView, custom_logout
from django.contrib.auth.views import LogoutView
from tasks.views import delete_task
from tasks.views import notifications_view




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
    path('calendar/data/', views.calendar_data, name='calendar_data'),
    path('tasks/<int:pk>/delete/', delete_task, name='delete_task'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/unread-count/', views.notifications_unread_count, name='notifications_unread_count'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('tasks/<int:pk>/complete/', views.complete_task, name='complete_task'),
]




