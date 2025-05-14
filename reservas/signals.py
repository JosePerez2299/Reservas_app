from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.conf import settings


# Mapeo de tus claves de modelo a (app_label, model_name)
MODEL_MAP = {
    'usuario': ('auth', 'user'),
    'espacio': ('reservas', 'espacio'),
    'reserva': ('reservas', 'reserva'),
}

@receiver(post_migrate)
def crear_grupos_y_permisos(sender, **kwargs):
    """
    Para cada grupo en DASHBOARD_ACCESS:
      1. Crear el grupo si no existe.
      2. Limpiar sus permisos actuales.
      3. Asignarle add/change/delete/view sobre cada modelo listado.
    """
    for nombre_grupo, modelos in settings.DASHBOARD_ACCESS.items():
        grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
        grupo.permissions.clear()

        for clave_modelo in modelos:
            # Obtén app_label y model_name según tu mapeo
            mapping = MODEL_MAP.get(clave_modelo)
            if not mapping:
                continue  # modelo desconocido, salta
            app_label, model_name = mapping

            # Intenta obtener el content type
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                continue  # el modelo aún no está migrado

            # Asigna los cuatro permisos CRUD
            for accion in ('add', 'change', 'delete', 'view'):
                codename = f"{accion}_{model_name}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    grupo.permissions.add(perm)
                except Permission.DoesNotExist:
                    # Si por algún motivo falta un permiso, lo omitimos
                    continue

        grupo.save()
