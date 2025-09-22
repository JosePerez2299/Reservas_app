from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from .services import enviar_email_confirmacion, enviar_email_aprobacion, enviar_email_rechazo
from apps.reservas.models import Reserva


@receiver(pre_save, sender=Reserva)
def reserva_estado_change_logger(sender, instance, **kwargs):
    """Imprime en consola cuando cambia el estado de una Reserva en un update."""
    if not instance.pk:
        enviar_email_confirmacion(instance)
        # Es una creación, no hay estado previo
        return
    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if anterior.estado != instance.estado:

        if instance.estado == Reserva.Estado.APROBADA:
            enviar_email_aprobacion(instance)
        elif instance.estado == Reserva.Estado.RECHAZADA:
            enviar_email_rechazo(instance)

