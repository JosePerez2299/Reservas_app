from apps.espacios.models import Espacio
from apps.reservas.models import DetalleReservaDigital, RequerimientoReserva, Reserva
from django import forms


class ReservaTipoForm(forms.Form):
    tipo = forms.ChoiceField(choices=Espacio.Tipo.choices, widget=forms.Select(
        attrs={"class": "select select-bordered"}))

        


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
            'usuario', 'espacio', 'fecha_uso',
            'hora_inicio', 'hora_fin',
            'motivo', 'numero_participantes'
        ]

    class Meta:
        model = Reserva
        fields = ['usuario', 'espacio', 'fecha_uso', 'hora_inicio',
                  'hora_fin', 'motivo', 'numero_participantes']


class DetalleReservaDigitalForm(forms.ModelForm):
    class Meta:
        model = DetalleReservaDigital
        fields = ['anfitrion_usuario',
                  'ubicacion_transmision', 'espacio_transmision']


class RequerimientoReservaForm(forms.ModelForm):
    class Meta:
        model = RequerimientoReserva
        fields = ['nombre', 'observacion', 'tipo']


class ReservaApproveForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado', 'mensaje_aprobar_rechazar']
