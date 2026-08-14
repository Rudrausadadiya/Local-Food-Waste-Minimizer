from django.apps import AppConfig


# Class: MarketplaceConfig
class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.marketplace'
    verbose_name = 'Marketplace Module'

    # Method: ready
    def ready(self):
        import importlib
        importlib.import_module('apps.marketplace.signals')
