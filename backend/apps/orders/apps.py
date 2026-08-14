from django.apps import AppConfig


# Class: OrdersConfig
class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Order & Sales Management'

    # Method: ready
    def ready(self):
        import importlib
        importlib.import_module('apps.orders.signals')
