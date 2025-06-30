from django import forms
from django.db.models import Q
from reservas.models import Reserva, Espacio, Usuario
from datetime import date, timedelta
from reservas.library.utils.form_widgets import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, Row
from django_select2.forms import Select2Widget

class ReservaCreateForm(forms.ModelForm, ):
    class Meta:
        model = Reserva
        fields = ['usuario', 'fecha_uso', 'hora_inicio',
                  'hora_fin', 'espacio', 'motivo', ]
        widgets = {
            'fecha_uso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'min': date.today().isoformat(), 'max': (
                    date.today() + timedelta(days=90)).isoformat()}
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'usuario': Select2Widget,
            'espacio': Select2Widget,
            'motivo_admin': forms.Textarea(attrs={'rows': 3, 'label': 'Motivo de gestion', 'placeholder': 'Motivo de gestion'}),
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


          # Helper y layout con Tailwind
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # IMPORTANTE: Desactivar el renderizado automático del form tag
        # ya que lo manejas manualmente en el template
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Field('usuario', css_class="input input-bordered p-2"),
                css_class="mb-4"
            ),
            Div(
                Field('espacio', css_class="input input-bordered w-full"),
                css_class="mb-4"
            ),
            Div(
                Field('fecha_uso', css_class="input input-bordered w-full"),
                css_class="mb-4"
            ),
            Row(
                Div(
                    Field('hora_inicio', css_class="input input-bordered w-full"),
                    css_class="w-1/2 mr-2"
                ),
                Div(
                    Field('hora_fin', css_class="input input-bordered w-full"),
                    css_class="w-1/2"
                )
            ),

            Div(
                Field('motivo', placeholder="Motivo de la reserva", css_class="h-24 resize-none textarea textarea-bordered w-full"),
                css_class="mb-6"
            ),

            Div(
                Submit('submit', 'Guardar', css_class="btn btn-primary w-full"),
            )
        )

class ReservaUpdateForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_uso', 'hora_inicio',
                  'hora_fin',  'motivo']
        widgets = {
            'fecha_uso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'min': date.today().isoformat(), 'max': (
                    date.today() + timedelta(days=90)).isoformat()}
            ),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'label': 'Motivo de gestion', 'placeholder': 'Motivo de gestion'}),
        }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        user = self.request.user
        super().__init__(*args, **kwargs)

        if user.is_usuario:
            self.fields['estado'].disabled = True
            self.fields['motivo_admin'].disabled = True

        if not user.is_admin and user.is_moderador:
            if self.instance.espacio.ubicacion != user.ubicacion or self.instance.espacio.piso != user.piso:
                self.fields['estado'].disabled = True
                self.fields['estado'].help_text = "No puedes aprobar o rechazar reservas de espacios de otra ubicación o piso"
        
        # Helper y layout con Tailwind
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                Field('fecha_uso', css_class="input input-bordered w-full"),
                css_class="mb-4"
            ),
            Row(
                Div(
                    Field('hora_inicio', css_class="input input-bordered w-full"),
                    css_class="w-1/2 mr-2"
                ),
                Div(
                    Field('hora_fin', css_class="input input-bordered w-full"),
                    css_class="w-1/2"
                )
            ),

            Div(
                Field('motivo', placeholder="Motivo de la reserva", css_class="h-24 resize-none textarea textarea-bordered w-full"),
                css_class="mb-6"
            ),

            Div(
                Submit('submit', 'Guardar', css_class="btn btn-primary w-full"),
            )
        )
    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        
        if estado in [Reserva.Estado.APROBADA, Reserva.Estado.RECHAZADA]:
            if hasattr(self, 'instance') and self.instance:
                self.instance.aprobado_por = self.request.user