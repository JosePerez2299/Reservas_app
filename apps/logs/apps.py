from django.apps import AppConfig


class LogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.logs'

    def ready(self):
        import apps.reservas.signals  
        from auditlog.registry import auditlog
        from apps.usuarios.models import Ubicacion  
        from apps.espacios.models import Espacio
        from apps.usuarios.models import Usuario
        from apps.reservas.models import Reserva
        auditlog.register(Reserva)
        auditlog.register(Usuario, exclude_fields=['password', 'last_login'])
        auditlog.register(Espacio)
        auditlog.register(Ubicacion)
        