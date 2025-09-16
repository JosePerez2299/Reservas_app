from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Ubicacion, PlataformaDigital    
from config.model_perms import DASHBOARD_ACCESS
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django_auth_ldap.backend import populate_user
import logging
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def assign_default_group_on_create(sender, instance, created, **kwargs):
    """
    Al crearse un usuario (created=True):
      - Si no tiene grupos asignados, le damos 'usuario' por defecto.
      - Si ya tiene 'administrador', no tocamos nada.
    Esto evita modificar usuarios creados manualmente en admin (si ya tienen grupos).
    """
    if not created:
        return

    try:
        # si ya tiene algún grupo (p.e. admin lo creó con grupos), no hacemos nada
        if instance.groups.exists():
            logger.debug("Nuevo usuario ya tiene grupos: %s", instance.username)
            return

        # buscar/crear grupo 'usuario' y añadirlo
        usuario_group, _ = Group.objects.get_or_create(name="usuario")
        instance.groups.add(usuario_group)
        logger.debug("Asignado grupo 'usuario' al nuevo usuario %s", instance.username)

    except Exception as e:
        logger.exception("Error al asignar grupo por defecto al usuario %s: %s", instance.username, e)

@receiver(post_migrate) 
def crear_grupos_y_permisos(sender, **kwargs):
    """
    Para cada grupo en model_perms:
      1. Crea el grupo (si no existe) y limpia sus permisos.
      2. Para cada modelo y cada acción listada en el dict, asigna ese permiso.
    """
    # Nombre de tu app donde están los modelos
    APP_LABEL = 'core'

    for nombre_grupo, modelos in DASHBOARD_ACCESS.items():
        grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
        grupo.permissions.clear()

        for modelo in modelos:  
            try:
                full_name = modelo['model']['name']
                app_label, model_name = full_name.split('.')
                Model = apps.get_model(app_label, model_name)
            except LookupError:
                continue

            # ContentType asociado
            try:
                ct = ContentType.objects.get_for_model(Model)
            except ContentType.DoesNotExist:
                continue

            # Itera sólo las acciones definidas en settings
            for accion in modelo['perms']:
                codename = f"{accion}_{Model._meta.model_name}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    grupo.permissions.add(perm)
                except Permission.DoesNotExist:
                    continue

        grupo.save()


@receiver(post_migrate)
def crear_ubicaciones(sender, **kwargs):
    APP_LABEL = 'core'

    ubicaciones = [
        'Nea',
        'Los Cortijos',
        'CET',
        'Los Palos Grandes',
        'La Yaguara',

    ]

    plataformas = [
        ('Google Meet', 'https://meet.google.com'),
        ('Zoom', 'https://zoom.us'),
        ('Teams', 'https://teams.microsoft.com'),
        ('Skype', 'https://www.skype.com'),
    ]

    for ubicacion in ubicaciones:
        Ubicacion.objects.get_or_create(nombre=ubicacion) 
    
    for plataforma in plataformas:
        PlataformaDigital.objects.get_or_create(nombre=plataforma[0], url=plataforma[1])