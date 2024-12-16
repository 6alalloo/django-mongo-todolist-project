from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = 'tasks'
    


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        import tasks.signals

class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals