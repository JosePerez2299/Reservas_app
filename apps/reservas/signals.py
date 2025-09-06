from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from apps.reservas.models import TipoActividad


@receiver(post_migrate)
def crear_grupos_y_permisos(sender, **kwargs):
    """
    Para cada grupo en settings.DASHBOARD_ACCESS:
      1. Crea el grupo (si no existe) y limpia sus permisos.
      2. Para cada modelo y cada acción listada en el dict, asigna ese permiso.
    """
    # Nombre de tu app donde están los modelos
    APP_LABEL = 'app.usuarios'

    for nombre_grupo, modelos in settings.DASHBOARD_ACCESS.items():
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
def crear_tipos_actividad(sender, **kwargs):
    
    tipos_actividad = [
    'Actividad política',
    'Actividades de Responsabilidad Social',
    'Asamblea',
    'Celebración de fecha conmemorativa',
    'Comité',
    'Conversatorio',
    'Curso',
    'Encuentro de gerentes',
    'Ensayo',   
    'Entrega de reconocimiento',
    'Entrega de servicio',
    'Entrevista',
    'Evento de patrocinio',
    'Evento electoral',
    'Evento presidencial',
    'Feria',
    'Formación',
    'Foro',
    'Grabación',
    'Graduación',
    'Inauguración',
    'Integración',  
    'Jornada',
    'Patrocinio',
    'Perifoneo',
    'Podcast',
    'Pregira',
    'Premiación',
    'Presentación de proyectos',        
    'Reunión de trabajo',
    'Ruedas de prensa',
    'Sinergia',
    'Taller',
    'Videoconfencia',
    'Visita guiadas',
    'Otros',
    ]

    for tipo_actividad in tipos_actividad:
        TipoActividad.objects.get_or_create(nombre=tipo_actividad)

