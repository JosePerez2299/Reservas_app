from django import forms
from django.db.models import Q
from reservas.models import Reserva, Espacio, Usuario
from datetime import date, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, Row

class ReservaCreateForm(forms.ModelForm ):
    class Meta:
        model = Reserva
        fields = ['usuario', 'fecha_uso', 'hora_inicio',
                  'hora_fin', 'espacio', 'motivo', ]
        widgets = {
            'usuario': forms.Select(attrs={'class': 'select2 form-select w-full'}),
            'fecha_uso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'min': date.today().isoformat(), 'max': (
                    date.today() + timedelta(days=90)).isoformat(), 'class': 'form-control w-full' }
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'fieldset_class': 'w-1/2 flex-1', 'class': 'form-control' }),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'fieldset_class': 'w-1/2 flex-1', 'class': 'form-control' }),
            'motivo': forms.Textarea(attrs={'rows': 3, 'label': 'Motivo de la reserva', 'placeholder': 'Motivo de la reserva',  'class': 'form-textarea'}),
            'espacio': forms.Select(attrs={'class': 'select2 form-select w-full'}),
            
            }

        help_texts = {
            'usuario': 'Requerido. 20 caracteres o menos. Debe comenzar con letra.',
        }
    
    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None)
        
        # Llamamos a la implementación original
        super().__init__(*args, **kwargs)

        # Configuración del usuario si es necesario
        user = self.request.user if self.request else None
        
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
        fields = [ 'fecha_uso', 'hora_inicio',
                  'hora_fin',  'motivo']
        widgets = {
            'fecha_uso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'min': date.today().isoformat(), 'max': (
                    date.today() + timedelta(days=90)).isoformat(), 'class': 'form-control w-full'}
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control w-full', 'fieldset_class': 'w-1/2 flex-1'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control w-full', 'fieldset_class': 'w-1/2 flex-1'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'label': 'Motivo de gestion', 'placeholder': 'Motivo de gestion', 'class': 'form-textarea w-full'}),
        }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        user = self.request.user
        super().__init__(*args, **kwargs)


class ReservaApproveForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado', 'motivo_admin', 'aprobado_por']
        widgets = {
            'estado' : forms.Select(attrs={ 'class': ' form-select w-full'}),
            'motivo_admin': forms.Textarea(attrs={ 'label': 'Motivo de gestion', 'placeholder': 'Motivo de gestion', 'class': 'form-textarea w-full'}),
            'aprobado_por': forms.HiddenInput(),
        }
    

    def clean_aprobado_por(self):
        return self.request.user

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        user = self.request.user
        super().__init__(*args, **kwargs)
        
        self.fields['aprobado_por'].initial = user.pk
        self.fields['aprobado_por'].disabled = True
        
        # Configurar el campo de estado solo con opciones de aprobación/rechazo
        self.fields['estado'].choices = [
            (Reserva.Estado.APROBADA, 'Aprobar'),
            (Reserva.Estado.RECHAZADA, 'Rechazar')
        ]
        
