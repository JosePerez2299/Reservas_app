import logging
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from .services import enviar_email_confirmacion, enviar_email_aprobacion, enviar_email_rechazo, rechazar_reservas_conflictivas
from apps.reservas.models import Reserva
from library.utils.async_calls import async_call


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Reserva)
def capturar_estado_anterior(sender, instance, **kwargs):
    """Captura el estado anterior antes de guardar, para compararlo en post_save."""
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = anterior.estado
        except sender.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=Reserva)
def reservas_post_save(sender, instance, created, **kwargs):
    """
    Maneja notificaciones por email y rechaza reservas conflictivas
    después de guardar la reserva.
    """
    if created:
        # Nueva reserva → enviar confirmación async
        async_call(enviar_email_confirmacion, instance)
        return

    estado_anterior = getattr(instance, "_estado_anterior", None)

    if estado_anterior and estado_anterior != instance.estado:
        if instance.estado == Reserva.Estado.APROBADA:
            # Notificación de aprobación async
            async_call(enviar_email_aprobacion, instance)

            # Rechazar conflictivas (con update masivo + correos async)
            async_call(
                rechazar_reservas_conflictivas,
                reserva_aprobada=instance,
                usuario=instance.aprobado_por,
            )

        elif instance.estado == Reserva.Estado.RECHAZADA:
            # Notificación de rechazo async
            async_call(enviar_email_rechazo, instance)
