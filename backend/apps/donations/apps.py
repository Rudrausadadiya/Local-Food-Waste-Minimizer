from django.apps import AppConfig


# Class: DonationsConfig
class DonationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.donations'
    verbose_name = 'NGO & Food Donation Module'

    # Method: ready
    def ready(self):
        import importlib
        importlib.import_module('apps.donations.signals')
