import logging
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from .services import enviar_email_confirmacion, enviar_email_aprobacion, enviar_email_rechazo, rechazar_reservas_conflictivas
from apps.reservas.models import Reserva

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Reserva)  
def reserva_rechazar_conflictos(sender, instance, created, **kwargs):
    """
    Signal para rechazar las reservas conflictivas automáticamente
    cuando una reserva se aprueba.
    """
    # Para creaciones
    if created:
        print("Creada nueva reserva, no hay que rechazar conflictivas")
        return
    
    # Para updates manuales, necesitamos el estado anterior
    # Lo obtenemos del pre_save anterior
    estado_anterior = getattr(instance, '_estado_anterior', None)
    
    if estado_anterior and estado_anterior != instance.estado:
        if instance.estado == Reserva.Estado.APROBADA:
            
            rechazar_reservas_conflictivas(reserva_aprobada=instance, usuario=instance.aprobado_por)


@receiver(pre_save, sender=Reserva)
def capturar_estado_anterior(sender, instance, **kwargs):
    """
    Captura el estado anterior antes de guardar,
    para compararlo en post_save.
    """
    print("Capturando estado anterior...")
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
        # Nueva reserva → enviar confirmación
        enviar_email_confirmacion(instance)
        return

    estado_anterior = getattr(instance, "_estado_anterior", None)

    if estado_anterior and estado_anterior != instance.estado:
        if instance.estado == Reserva.Estado.APROBADA:
            # Notificación de aprobación
            enviar_email_aprobacion(instance)

            # Rechazar conflictivas (con update masivo + correos manuales)
            rechazar_reservas_conflictivas(
                reserva_aprobada=instance,
                usuario=instance.aprobado_por,
            )

        elif instance.estado == Reserva.Estado.RECHAZADA:
            # Notificación de rechazo
            enviar_email_rechazo(instance)
