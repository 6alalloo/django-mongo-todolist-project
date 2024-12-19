from django.contrib import admin
from .models import Task, Notification



admin.site.site_header = 'To Do List Admin - 6alal'
admin.site.register(Task)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
