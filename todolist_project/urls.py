
from django.contrib import admin
from django.urls import include, path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),
]
