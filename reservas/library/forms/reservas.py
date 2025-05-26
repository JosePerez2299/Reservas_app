from django import forms
from reservas.models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['usuario', 'fecha_uso', 'hora_inicio', 'hora_fin', 'espacio', 'motivo']
        widgets = {
            'fecha_uso': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }
