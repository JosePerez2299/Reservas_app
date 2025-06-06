from django.apps import AppConfig


class ReservasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservas'
    def ready(self):
        import reservas.signals  
        from auditlog.registry import auditlog
        from .models import Reserva, Usuario, Espacio, Ubicacion
        auditlog.register(Reserva)
        auditlog.register(Usuario, exclude_fields=['last_login'])
        auditlog.register(Espacio)
        auditlog.register(Ubicacion)
        