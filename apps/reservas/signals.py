import logging
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from .services import enviar_email_admin_conflictos, enviar_email_confirmacion, enviar_email_aprobacion, enviar_email_rechazo, enviar_email_rechazo_automatico, rechazar_reservas_conflictivas
from apps.reservas.models import Reserva

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Reserva)
def reserva_logica_negocio(sender, instance, **kwargs):
    """
    Signal SOLO para lógica de negocio.
    Se ejecuta ANTES de guardar.
    """
    
    # ⚠️ EVITAR RECURSIÓN: No procesar rechazos automáticos
    if getattr(instance, '_es_rechazo_automatico', False):
        return
    
    if not instance.pk:
        return
        
    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
        
    if anterior.estado != instance.estado:
        if instance.estado == Reserva.Estado.APROBADA:
            logger.info(f"Procesando aprobación de reserva {instance.id}")
            
            # ✅ SOLO lógica de negocio aquí
            conflictivas_rechazadas = rechazar_reservas_conflictivas(
                usuario=instance.aprobado_por, 
                reserva_aprobada=instance
            )
            
            # Guardar info para usar en notificaciones
            instance._conflictivas_rechazadas = conflictivas_rechazadas


@receiver(post_save, sender=Reserva)  
def reserva_notificaciones(sender, instance, created, **kwargs):
    """
    Signal SOLO para notificaciones.
    Se ejecuta DESPUÉS de guardar (más seguro para emails).
    """
    
    # Para creaciones
    if created:
        enviar_email_confirmacion(instance)
        return
    
    # ⚠️ MANEJAR RECHAZOS AUTOMÁTICOS: Enviar email específico
    if getattr(instance, '_es_rechazo_automatico', False):
        usuario_que_aprobo = getattr(instance, '_usuario_que_aprobo', None)
        enviar_email_rechazo_automatico(instance, usuario_que_aprobo)
        return
    
    # Para updates manuales, necesitamos el estado anterior
    # Lo obtenemos del pre_save anterior
    estado_anterior = getattr(instance, '_estado_anterior', None)
    
    if estado_anterior and estado_anterior != instance.estado:
        if instance.estado == Reserva.Estado.APROBADA:
            enviar_email_aprobacion(instance)
            
            # Notificar sobre conflictivas rechazadas si las hay
            conflictivas_rechazadas = getattr(instance, '_conflictivas_rechazadas', 0)
            if conflictivas_rechazadas > 0:
                enviar_email_admin_conflictos(instance, conflictivas_rechazadas)
                
        elif instance.estado == Reserva.Estado.RECHAZADA:
            enviar_email_rechazo(instance)


# Signal helper para capturar estado anterior
@receiver(pre_save, sender=Reserva)
def capturar_estado_anterior(sender, instance, **kwargs):
    """Helper para capturar estado anterior para post_save"""
    if instance.pk and not getattr(instance, '_es_rechazo_automatico', False):
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = anterior.estado
        except sender.DoesNotExist:
            instance._estado_anterior = None