from django.urls import path
from . import views


urlpatterns = [
    path('',views.home, name='home'),
    path('tasks', views.tasks_view, name='tasks'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('signup/', views.signup_view, name='signup'),
]




