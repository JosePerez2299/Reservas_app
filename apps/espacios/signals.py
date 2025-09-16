from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Espacio

@receiver(pre_save, sender=Espacio)
def rechazar_reservas_al_cambiar_disponibilidad(sender, instance, **kwargs):
    # Solo ejecutar si el espacio ya existe y cambió de disponible a no disponible
    if instance.pk:
        try:
            espacio_anterior = Espacio.objects.get(pk=instance.pk)
            # Si cambió de disponible=True a disponible=False
            if espacio_anterior.disponible and not instance.disponible:
                ahora = timezone.now()
                print("Disponibilidad cambiada a False", instance)
                # # Rechazar reservas pendientes
                # Reserva.objects.filter(
                #     espacio=instance,
                #     estado='pendiente'
                # ).update(estado='rechazada')
                
                # # Cancelar reservas aprobadas futuras
                # Reserva.objects.filter(
                #     espacio=instance,
                #     estado='aprobada',
                #     fecha_inicio__gt=ahora
                # ).update(estado='cancelada')
                
        except Espacio.DoesNotExist:
            pass