from django import forms
from django.db.models import Q
from reservas.models import Reserva, Usuario

class ReservaCreateForm(forms.ModelForm):
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

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        # Si es moderador o administrador, mostrar selector de usuarios
        if self.request.user.is_moderador or self.request.user.is_admin:
            self.fields['usuario'].queryset = Usuario.objects.all()
        # Si es usuario normal, mostrar campo deshabilitado con su usuario
        elif self.request.user.is_usuario:
            self.fields['usuario'].queryset = Usuario.objects.filter(pk=self.request.user.pk)
            self.fields['usuario'].initial = self.request.user
            self.fields['usuario'].disabled = True
            self.fields['usuario'].help_text = "No puedes cambiar este campo"
            