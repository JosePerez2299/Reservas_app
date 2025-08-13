from auditlog.models import LogEntry
from django_filters import  FilterSet
from django import forms
from django_filters import CharFilter, DateFilter, ChoiceFilter
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field

class LogFilter(FilterSet):
    actor = CharFilter(
        field_name='actor__username',
        lookup_expr='icontains',
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por usuario…',
            'id': 'actor_filter'
        })
    )
    timestamp = DateFilter(
        field_name='timestamp',
        lookup_expr='icontains',
        label='Fecha',
        widget=forms.DateInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary',
            'type': 'date'
        })
    )

    tipo = ChoiceFilter(
        field_name='tipo',
        lookup_expr='iexact',
        label='Modulo',
        choices=[
            ('Usuario', 'Usuario'),
            ('Espacio', 'Espacio'),
            ('Reserva', 'Reserva'),
        ]
    )
    action_label = ChoiceFilter(
        field_name='action_label',     
        lookup_expr='iexact',
        label='Tipo de acción',
        choices=[
            ('Crear', 'Crear'),
            ('Actualizar', 'Actualizar'),
            ('Eliminar', 'Eliminar'),
        ],
    )
    class Meta:
        model = LogEntry
        fields = ['actor', 'tipo', 'action_label', 'timestamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.form_method = 'get'
        self.form.helper.form_class = 'form-inline'
        self.form.helper.layout = Layout(
            Div(
                Field('actor'),
                Field('tipo'),
                Field('action_label'),
                Field('timestamp'),
                Submit('search', 'Buscar', css_class='btn-primary'),
            )
        )