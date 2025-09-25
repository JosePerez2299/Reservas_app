from django.db import transaction
from django.utils import timezone
from apps.espacios.forms import EspacioForm, DetalleFisicoForm, DetalleDigitalForm
from apps.espacios.models import Espacio
from apps.reservas.models import Reserva

def rechazar_reservas_por_indisponibilidad(espacio):
    '''
    Rechaza todas las reservas pendientes, aprobadas que incluyen el espacio dado
    en la fecha actual o futura.    
    '''
    try:
        fecha_actual = timezone.now().date()
        reservas_que_incluyen_espacio = Reserva.objects.filter(
            espacios=espacio,
            fecha_uso__gte=fecha_actual,
            estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA]
        ).update(
            estado=Reserva.Estado.RECHAZADA,
            mensaje_aprobar_rechazar="Rechazada automáticamente por indisponibilidad del espacio."
        )   

        print(f"Reservas actualizadas: {reservas_que_incluyen_espacio}")
    except Exception as e:
        
        print("No se encontraron reservas que incluyan el espacio.", e)
        return




def create_espacio(espacio_form: EspacioForm, detalle_form: DetalleFisicoForm | DetalleDigitalForm):
    """
    Crea un espacio en la base de datos y un detalle en la base de datos
    """
    with transaction.atomic():
        espacio = espacio_form.save()
        detalle = detalle_form.save(commit=False)
        detalle.espacio_id = espacio.id
        detalle.save()

    return espacio


def es_espacio_digital(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('espacio') or {}
    return cleaned_data.get('tipo') == Espacio.Tipo.DIGITAL


def es_espacio_fisico(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('espacio') or {}
    return cleaned_data.get('tipo') == Espacio.Tipo.FISICO

