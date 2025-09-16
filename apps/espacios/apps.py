from django.apps import AppConfig


class EspaciosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.espacios'
    def ready(self):
        import apps.espacios.signals 