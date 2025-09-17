from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from apps.reservas.models import Reserva


@receiver(pre_save, sender=Reserva)
def reserva_estado_change_logger(sender, instance, **kwargs):
    """Imprime en consola cuando cambia el estado de una Reserva en un update."""
    if not instance.pk:
        # Es una creación, no hay estado previo
        return
    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if anterior.estado != instance.estado:
        print(f"[Reserva] Cambio de estado: id={instance.pk} {anterior.estado} -> {instance.estado}")

