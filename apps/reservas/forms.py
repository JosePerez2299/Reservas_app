from django.urls import reverse
from apps.espacios.models import Espacio
from apps.reservas.models import DetalleReservaDigital, Reserva
from apps.usuarios.models import Usuario

from django import forms

# Selecciona el usuario que va a realizar la reserva
class ContactoForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.all(),
        widget=forms.Select(
            attrs={"class": "select select-bordered"}
        )
    )

class ReservaTipoForm(forms.ModelForm):
    modalidad = forms.ChoiceField(choices=Reserva.Modalidad.choices, widget=forms.Select(
        attrs={"class": "select select-bordered"}))

    tipo_solicitud = forms.ChoiceField(choices=Reserva.TipoSolicitud.choices, widget=forms.Select(
        attrs={"class": "select select-bordered"}))

    fecha_uso = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date"}
        )
    )

    p00_solicitante = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "input "}
        )
    )
    class Meta:
        model = Reserva
        fields = ['modalidad', 'tipo_solicitud', 'p00_solicitante', 'fecha_uso']

class ReservaCreateForm(forms.ModelForm):
    espacio = forms.ModelChoiceField(
        queryset=Espacio.objects.all(),
        widget=forms.Select(
            attrs={"class": "select select-bordered"}
        )
    )
    fecha_uso = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "date-input", "type": "date"}
        )
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"class": "time-input", "type": "time"}
        )
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(
            attrs={"class": "time-input", "type": "time"}
        )
    )

    class Meta:
        model = Reserva
        fields = [
            'p00_solicitante', 'espacio', 'fecha_uso',
            'hora_inicio', 'hora_fin',
            'motivo', 
        ]



class DetalleReservaDigitalForm(forms.ModelForm):
    class Meta:
        model = DetalleReservaDigital
        fields = ['anfitrion_usuario',
                  'ubicacion_transmision', 'espacio_transmision']



class ReservaApproveForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado', 'mensaje_aprobar_rechazar']
