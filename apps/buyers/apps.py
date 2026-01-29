from django.apps import AppConfig


class BuyersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.buyers'
    
    def ready(self):
        import apps.buyers.signals
