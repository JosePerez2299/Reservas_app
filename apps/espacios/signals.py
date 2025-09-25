from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.espacios.services import rechazar_reservas_por_indisponibilidad
from library.utils.async_calls import async_call
from .models import Espacio

@receiver(pre_save, sender=Espacio)
def rechazar_reservas_al_cambiar_disponibilidad(sender, instance, **kwargs):
    # Solo ejecutar si el espacio ya existe y cambió de disponible a no disponible
    if instance.pk:
        try:
            espacio_anterior = Espacio.objects.get(pk=instance.pk)
            # Si cambió de disponible=True a disponible=False
            if espacio_anterior.disponible and not instance.disponible:
                async_call(rechazar_reservas_por_indisponibilidad, instance)
                
        except Espacio.DoesNotExist:
            pass