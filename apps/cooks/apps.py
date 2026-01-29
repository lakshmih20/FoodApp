from django.apps import AppConfig


class CooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cooks'
    
    def ready(self):
        import apps.cooks.signals
