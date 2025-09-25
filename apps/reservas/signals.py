import logging
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from .services import enviar_email_confirmacion, enviar_email_aprobacion, enviar_email_rechazo, rechazar_reservas_conflictivas
from apps.reservas.models import Reserva

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Reserva)
def reservas_notificaciones(sender, instance, **kwargs):
    """
    Signal para enviar notificaciones por email cuando una reserva cambia de estado.
    """
    if not instance.pk:
        enviar_email_confirmacion(instance)
        return
        
    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    
    estado_anterior = anterior.estado
    estado_actual = instance.estado
    if estado_anterior == Reserva.Estado.PENDIENTE  and estado_anterior != estado_actual:
        if instance.estado == Reserva.Estado.APROBADA:
            enviar_email_aprobacion(instance)
                
        elif instance.estado == Reserva.Estado.RECHAZADA:
            enviar_email_rechazo(instance)


@receiver(post_save, sender=Reserva)  
def reserva_rechazar_conflictos(sender, instance, created, **kwargs):
    """
    Signal para rechazar las reservas conflictivas automáticamente
    cuando una reserva se aprueba.
    """
    # Para creaciones
    if created:
        return
    
    # Para updates manuales, necesitamos el estado anterior
    # Lo obtenemos del pre_save anterior
    estado_anterior = getattr(instance, '_estado_anterior', None)
    
    if estado_anterior and estado_anterior != instance.estado:
        if instance.estado == Reserva.Estado.APROBADA:
            
            rechazar_reservas_conflictivas(reserva_aprobada=instance, usuario=instance.aprobado_por)


# Signal helper para capturar estado anterior
@receiver(pre_save, sender=Reserva)
def capturar_estado_anterior(sender, instance, **kwargs):
    """Helper para capturar estado anterior para post_save"""
    if instance:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = anterior.estado
        except sender.DoesNotExist:
            instance._estado_anterior = None