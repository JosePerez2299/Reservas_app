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
        user = self.request.user
        super().__init__(*args, **kwargs)

        # Filtrar espacios disponibles
        self.fields['espacio'].queryset = Espacio.objects.filter(
            Q(disponible=True)
        )
        
        # Si es administrador, mostrar selector de usuarios del grupo moderador y usuario, o su mismo id
        if user.is_admin:
            self.fields['usuario'].queryset = Usuario.objects.filter(
                Q(groups__name=user.GRUPOS.USUARIO) | Q(groups__name=user.GRUPOS.MODERADOR) | Q(id=user.id))

        # Si es moderador, mostrar selector de usuarios del grupo usuario 
        elif user.is_moderador:
            self.fields['usuario'].queryset = Usuario.objects.filter(
                (
                    Q(groups__name=user.GRUPOS.USUARIO) &
                    Q(ubicacion=user.ubicacion) &
                    Q(piso=user.piso)
                ) | Q(id=user.id)
            )

        # Si es usuario, mostrar selector de su usuario
        elif user.is_usuario:
            self.fields['usuario'].initial = user
            self.fields['usuario'].disabled = True
            self.fields['usuario'].help_text = "No puedes cambiar este campo"

class ReservaUpdateForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['usuario', 'fecha_uso', 'hora_inicio',
                  'hora_fin', 'espacio', 'motivo', 'estado', 'motivo_admin']
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
            'motivo_admin': forms.Textarea(attrs={'rows': 3, 'label': 'Motivo de gestion', 'placeholder': 'Motivo de gestion'}),
        }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        user = self.request.user
        super().__init__(*args, **kwargs)

        self.fields['usuario'].disabled = True
        self.fields['espacio'].disabled = True

        self.fields['usuario'].help_text = "No puedes cambiar este campo"
        self.fields['espacio'].help_text = "No puedes cambiar este campo"

        
        if user.is_usuario:
            self.fields['estado'].disabled = True

        if not user.is_admin and user.is_moderador:
            if self.instance.espacio.ubicacion != user.ubicacion or self.instance.espacio.piso != user.piso:
                self.fields['estado'].disabled = True
                self.fields['estado'].help_text = "No puedes aprobar o rechazar reservas de espacios de otra ubicación o piso"

    def save(self, commit=True):
        # Primero, instancia sin guardar aún
        instance = super().save(commit=False)
        
        user = self.request.user
        if instance.estado == Reserva.Estado.APROBADA or instance.estado == Reserva.Estado.RECHAZADA:
            instance.aprobado_por = user
        
        # Ahora sí guardamos
        if commit:
            instance.save()
        return instance 