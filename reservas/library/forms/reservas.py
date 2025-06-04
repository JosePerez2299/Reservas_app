from django import forms
from django.db.models import Q
from reservas.models import Reserva, Espacio, Usuario
from datetime import date, timedelta
from django_select2.forms import Select2Widget
from reservas.library.utils.form_widgets import *


class ReservaCreateForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['usuario', 'fecha_uso', 'hora_inicio',
                  'hora_fin', 'espacio', 'motivo']
        widgets = {
            'fecha_uso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'min': date.today().isoformat(), 'max': (
                    date.today() + timedelta(days=90)).isoformat()}
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'usuario': UsuarioWidget,
            'espacio': Select2Widget,
                }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        # Filtrar espacios disponibles
        self.fields['espacio'].queryset = Espacio.objects.filter(
            Q(disponible=True)
        )
        
        # Si es administrador, mostrar selector de usuarios del grupo moderador y usuario, o su mismo id
        if self.request.user.is_admin:
            self.fields['usuario'].queryset = Usuario.objects.filter(
                Q(groups__name='usuario') | Q(groups__name='moderador') | Q(id=self.request.user.id))

        # Si es moderador, mostrar selector de usuarios del grupo usuario 
        elif self.request.user.is_moderador:
            self.fields['usuario'].queryset = Usuario.objects.filter(
                (
                    Q(groups__name='usuario') &
                    Q(ubicacion=self.request.user.ubicacion) &
                    Q(piso=self.request.user.piso)
                ) | Q(id=self.request.user.id)
            )

        # Si es usuario, mostrar selector de su usuario
        elif self.request.user.is_usuario:
            self.fields['usuario'].initial = self.request.user
            self.fields['usuario'].disabled = True
            self.fields['usuario'].help_text = "No puedes cambiar este campo"

class ReservaUpdateForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['usuario', 'fecha_uso', 'hora_inicio',
                  'hora_fin', 'espacio', 'motivo', 'estado']
        widgets = {
            'fecha_uso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'min': date.today().isoformat(), 'max': (
                    date.today() + timedelta(days=90)).isoformat()}
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'usuario': UsuarioWidget,
            'espacio': Select2Widget,
        }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.fields['usuario'].disabled = True
        self.fields['espacio'].disabled = True

        self.fields['usuario'].help_text = "No puedes cambiar este campo"
        self.fields['espacio'].help_text = "No puedes cambiar este campo"

        
        if self.request.user.is_usuario:
            self.fields['estado'].disabled = True
            self.fields['estado'].widget = forms.HiddenInput()

        if not self.request.user.is_admin and self.request.user.is_moderador:
            if self.instance.espacio.ubicacion != self.request.user.ubicacion or self.instance.espacio.piso != self.request.user.piso:
                self.fields['estado'].disabled = True
                self.fields['estado'].help_text = "No puedes aprobar o rechazar reservas de espacios de otra ubicación o piso"

            self.fields['usuario'].queryset = Usuario.objects.filter(
                Q(ubicacion=self.request.user.ubicacion) & Q(piso=self.request.user.piso)
            )

    def save(self, commit=True):
        # Primero, instancia sin guardar aún
        instance = super().save(commit=False)
        print(instance.estado)
        print(self.request.user)
        if instance.estado == 'aprobada ' or instance.estado == 'rechazada':
            print("entro")
            instance.aprobado_por = self.request.user
        
        # Ahora sí guardamos
        if commit:
            instance.save()
        return instance