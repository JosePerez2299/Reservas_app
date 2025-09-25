from datetime import timezone
import logging
from django.conf import settings
from django.db.models import Q
from apps.reservas.models import Reserva, ReservaEspacio
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)

def rechazar_reservas_conflictivas(usuario, reserva_aprobada):
    """
    Rechaza automáticamente reservas conflictivas con la aprobada.
    Usa update() para evitar recursion de señales,
    y envía los correos manualmente.
    
    Args:
        usuario: Usuario que aprobó la reserva
        reserva_aprobada: Instancia de Reserva que se acaba de aprobar
    """
    now = timezone.now()

    # PASO 1: Query para encontrar conflictivas 
    conflictivas_query = Reserva.objects.filter(
        estado=Reserva.Estado.PENDIENTE,
        fecha_uso=reserva_aprobada.fecha_uso,
        hora_inicio__lt=reserva_aprobada.hora_fin,
        hora_fin__gt=reserva_aprobada.hora_inicio,
        espacios__in=reserva_aprobada.espacios.all()
    ).exclude(
        id=reserva_aprobada.id
    ).distinct()

    if not conflictivas_query.exists():
        return 0

    # PASO 2: Convertir a lista (para poder iterar después de update)
    conflictivas_list = list(conflictivas_query)

    # PASO 3: Update masivo (sin signals)
    updated_count = conflictivas_query.update(
        estado=Reserva.Estado.RECHAZADA,
        aprobado_por=usuario,
        fecha_cambio_estado=now,
        mensaje_aprobar_rechazar="Rechazada automáticamente por conflicto con otra reserva aprobada."
    )

    # PASO 4: Enviar correos manualmente
    for reserva in conflictivas_list:
        try:
            enviar_email_rechazo(reserva)
        except Exception as e:
            logger.error(f"Error enviando correo de rechazo para reserva {reserva.pk}: {e}")

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

    print(f"📧 Email confirmación enviado a {reserva.email_solicitante}, reserva: {reserva.id}")
    subject = "Confirmación de Reserva: "+ reserva.p00_solicitante
    message = f"Estimado {reserva.nombre_solicitante}.\nSu reserva con ID {reserva.id} ha sido creada y está pendiente de aprobación.\n\nDetalles:\nFecha: {reserva.fecha_uso}\nHora: {reserva.hora_inicio} - {reserva.hora_fin}\nModalidad: {reserva.get_modalidad_display()}"
    message += f"\nEspacio\\s: {', '.join([espacio.nombre for espacio in reserva.espacios.all()])}"
    
    recipient_list = [reserva.email_solicitante]
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

def enviar_email_aprobacion(reserva):
    """Email para reservas aprobadas manualmente"""
    print(f"✅ Email aprobación enviado a {reserva.email_solicitante}, reserva: {reserva.id}")
    subject = "Reserva aprobada. "  + reserva.p00_solicitante
    message = f"Estimado {reserva.nombre_solicitante}.\nSu reserva con ID {reserva.id} ha sido aprobada.\n\nDetalles:\nFecha: {reserva.fecha_uso}\nHora: {reserva.hora_inicio} - {reserva.hora_fin}\nModalidad: {reserva.get_modalidad_display()}"

    message += f"\nEspacio\\s: {', '.join([espacio.nombre for espacio in reserva.espacios.all()])}"
    if reserva.mensaje_aprobar_rechazar:
        message += f"\n\nMensaje adicional:\n{reserva.mensaje_aprobar_rechazar}"
    recipient_list = [reserva.email_solicitante]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
def enviar_email_rechazo(reserva):
    """Email para reservas rechazadas manualmente"""
    print(f"❌ Email rechazo enviado a {reserva.email_solicitante}, reserva: {reserva.id}")
    subject = "Reserva Rechazada: " + reserva.p00_solicitante
    message = f"Estimado {reserva.nombre_solicitante}.\nLamento informar que su reserva con ID {reserva.id} ha sido rechazada.\n\nDetalles:\nFecha: {reserva.fecha_uso}\nHora: {reserva.hora_inicio} - {reserva.hora_fin}\nModalidad: {reserva.get_modalidad_display()}"
    message += f"\nEspacio\\s: {', '.join([espacio.nombre for espacio in reserva.espacios.all()])}"

    if reserva.mensaje_aprobar_rechazar:
        message += f"\n\nMensaje adicional:\n{reserva.mensaje_aprobar_rechazar}"
    recipient_list = [reserva.email_solicitante]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )