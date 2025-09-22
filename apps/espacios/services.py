from django.db import transaction
from apps.espacios.forms import EspacioForm, DetalleFisicoForm, DetalleDigitalForm
from apps.espacios.models import Espacio


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

