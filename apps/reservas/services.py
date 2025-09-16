

from django.db.models import Q
from apps.reservas.models import Reserva


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

