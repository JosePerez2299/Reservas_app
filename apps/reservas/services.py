from datetime import timezone
import logging
from django.db.models import Q
from apps.reservas.models import Reserva, ReservaEspacio

from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)

def rechazar_reservas_conflictivas(usuario, reserva_aprobada):
    """
    Rechaza automáticamente reservas conflictivas con la aprobada.
    MODIFICADO para usar save() individual y disparar signals.
    
    Args:
        usuario: Usuario que aprobó la reserva
        reserva_aprobada: Instancia de Reserva que se acaba de aprobar
    """
    
    now = timezone.now()
    
    # PASO 1: Query  para encontrar conflictivas 
    conflictivas_query = Reserva.objects.filter(
        estado=Reserva.Estado.PENDIENTE,
        fecha_uso=reserva_aprobada.fecha_uso,
        hora_inicio__lt=reserva_aprobada.hora_fin,
        hora_fin__gt=reserva_aprobada.hora_inicio,
        espacios__in=reserva_aprobada.espacios.all()
    ).exclude(
        id=reserva_aprobada.id
    ).distinct()
    
    # Verificar si hay conflictos
    if not conflictivas_query.exists():
        return 0
    
    # PASO 2: Convertir a lista para evitar problemas con el queryset
    conflictivas_list = list(conflictivas_query)
    
    # PASO 3: Actualizar individualmente para disparar signals
    updated_count = 0
    
    for reserva in conflictivas_list:
        try:
            # Actualizar campos
            reserva.estado = Reserva.Estado.RECHAZADA
            reserva.aprobado_por = usuario
            reserva.fecha_cambio_estado = now
            reserva.mensaje_aprobar_rechazar = "Rechazada automáticamente por conflicto con otra reserva aprobada."
            
            reserva.save(update_fields=['estado', 'aprobado_por', 'fecha_cambio_estado', 'mensaje_aprobar_rechazar'])
            
            updated_count += 1
            
        except Exception as e:
            logger.error(f"Error rechazando reserva {reserva.pk}: {e}")
    
    logger.info(f"Rechazadas automáticamente {updated_count} reservas conflictivas")
    return updated_count

def lista_reservas_usuario(user, qs=None):
    """Devuelve un queryset de reservas según el rol del usuario.

    - Admin: todas las reservas
    - No admin: solo las del solicitante (p00 del usuario)
    """
    base_qs = qs if qs is not None else Reserva.objects.all()
    condiciones = Q() if getattr(user, 'is_admin', False) else Q(p00_solicitante=getattr(user, 'p00', None))
    return base_qs.filter(condiciones)


def es_reserva_presencial(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('reserva') or {}
    return cleaned_data.get('modalidad') == Reserva.Modalidad.PRESENCIAL

def es_reserva_virtual(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('reserva') or {}
    return cleaned_data.get('modalidad') == Reserva.Modalidad.VIRTUAL

def es_reserva_mixta(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('reserva') or {}
    return cleaned_data.get('modalidad') == Reserva.Modalidad.MIXTA

def es_presencial_o_mixta(wizard):
    """Muestra el paso de requerimientos si la modalidad es presencial o mixta"""
    cleaned_data = wizard.get_cleaned_data_for_step('reserva') or {}
    modalidad = cleaned_data.get('modalidad')
    return modalidad in [Reserva.Modalidad.PRESENCIAL, Reserva.Modalidad.MIXTA]

def es_virtual_o_mixta(wizard):
    """Muestra el paso de requerimientos si la modalidad es presencial o mixta"""
    cleaned_data = wizard.get_cleaned_data_for_step('reserva') or {}
    modalidad = cleaned_data.get('modalidad')
    return modalidad in [Reserva.Modalidad.VIRTUAL, Reserva.Modalidad.MIXTA]

def enviar_email_confirmacion(reserva):
    """Email para nuevas reservas creadas"""
    print(f"📧 Email confirmación enviado a {reserva.email_solicitante}")

def enviar_email_aprobacion(reserva):
    """Email para reservas aprobadas manualmente"""
    print(f"✅ Email aprobación enviado a {reserva.email_solicitante}, reserva: {reserva.id}")

def enviar_email_rechazo(reserva):
    """Email para reservas rechazadas manualmente"""
    print(f"❌ Email rechazo enviado a {reserva.email_solicitante}, reserva: {reserva.id}")