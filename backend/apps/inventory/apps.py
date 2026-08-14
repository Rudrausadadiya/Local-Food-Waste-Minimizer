from django.apps import AppConfig


# Class: InventoryConfig
class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'
    verbose_name = 'Inventory Management'

    # Method: ready
    def ready(self):
        import importlib
        importlib.import_module('apps.inventory.signals')
