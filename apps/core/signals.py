from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Ubicacion, PlataformaDigital    

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