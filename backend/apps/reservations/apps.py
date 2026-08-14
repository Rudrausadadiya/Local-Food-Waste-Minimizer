from django.apps import AppConfig


# Class: ReservationsConfig
class ReservationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reservations'
    verbose_name = 'Reservation Management'

    # Method: ready
    def ready(self):
        import importlib
        importlib.import_module('apps.reservations.signals')
