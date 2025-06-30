from auditlog.models import LogEntry
from django_filters import  FilterSet
from django import forms
from django_filters import CharFilter, DateFilter
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
        label='Fecha de uso',
        widget=forms.DateInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary',
            'type': 'date'
        })
    )

    class Meta:
        model = LogEntry
        fields = ['actor', 'timestamp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 1. Crear el helper
        self.form.helper = FormHelper()
        self.form.helper.form_method = 'get'
        self.form.helper.form_class = 'space-y-4 p-4 border rounded-lg'
        self.form.helper.label_class = 'font-semibold'
        self.form.helper.field_class = 'w-full'

        # 2. Definir el layout en filas y columnas
        self.form.helper.layout = Layout(
            Div(
                Field('actor', css_class='w-full'),
                css_class='w-full',
            ),
            Div(
                Field('timestamp', css_class='calendar w-full'),
                css_class='w-full',
            ),
           
            Submit('submit', 'Filtrar', css_class='btn btn-primary w-full mt-4')
        )

    def get_queryset(self):
        qs = super().get_queryset()
        return qs