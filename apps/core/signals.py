from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Ubicacion

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

    for ubicacion in ubicaciones:
        Ubicacion.objects.get_or_create(nombre=ubicacion)