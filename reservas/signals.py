from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def crear_grupos_y_permisos(sender, **kwargs):
    """
    Para cada grupo en settings.DASHBOARD_ACCESS:
      1. Crea el grupo (si no existe) y limpia sus permisos.
      2. Para cada modelo y cada acción listada en el dict, asigna ese permiso.
    """
    # Nombre de tu app donde están los modelos
    APP_LABEL = 'reservas'

    for nombre_grupo, modelos in settings.DASHBOARD_ACCESS.items():
        grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
        grupo.permissions.clear()

        for modelo_name, acciones in modelos.items():
            try:
                    Model = apps.get_model(APP_LABEL if modelo_name != "LogEntry" else "auditlog", modelo_name)
            except LookupError:
                continue

            # ContentType asociado
            try:
                ct = ContentType.objects.get_for_model(Model)
            except ContentType.DoesNotExist:
                continue

            # Itera sólo las acciones definidas en settings
            for accion in acciones['perms']:
                codename = f"{accion}_{Model._meta.model_name}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    grupo.permissions.add(perm)
                except Permission.DoesNotExist:
                    continue

        grupo.save()
