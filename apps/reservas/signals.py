from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from apps.reservas.models import TipoActividad

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

