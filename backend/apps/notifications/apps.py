from django.apps import AppConfig


# Class: NotificationsConfig
class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notification & Communication'

    # Method: ready
    def ready(self):
        import importlib
        importlib.import_module('apps.notifications.signals')
