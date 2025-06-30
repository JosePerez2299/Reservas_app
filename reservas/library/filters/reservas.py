import django_filters
from reservas.models import Reserva, Ubicacion
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, Field

class ReservaFilter(django_filters.FilterSet):
    usuario = django_filters.CharFilter(
        field_name='usuario__username',
        lookup_expr='exact',
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de usuario…',
            'id': 'username_filter'
        })
    )
    ubicacion = django_filters.ModelChoiceFilter(
        field_name='espacio__ubicacion',
        lookup_expr='exact',
        label='Ubicación',
        widget=forms.Select(attrs={
            'class': 'form-select'  ,
            'id': 'ubicacion_filter'
        }),
        queryset=Ubicacion.objects.all()
    )
    piso = django_filters.NumberFilter(
        field_name='espacio__piso',
        lookup_expr='exact',
        label='Piso',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    espacio = django_filters.CharFilter(
        field_name='espacio__nombre',
        lookup_expr='icontains',
        label='Espacio',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de espacio…',
            'id': 'espacio_filter'
        })
    )
    fecha_uso = django_filters.DateFilter(
        field_name='fecha_uso',
        lookup_expr='exact',
        label='Fecha de uso',
        widget=forms.DateInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary',
            'type': 'date'
        })
    )
    hora_inicio = django_filters.TimeFilter(
        field_name='hora_inicio',
        lookup_expr='gte',
        label='Hora de inicio',
        widget=forms.TimeInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary',
            'type': 'time'
        })
    )
    hora_fin = django_filters.TimeFilter(
        field_name='hora_fin',
        lookup_expr='lte',
        label='Hora de fin',
        widget=forms.TimeInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary',
            'type': 'time'
        })
    )
    estado = django_filters.ChoiceFilter(
        field_name='estado',
        lookup_expr='icontains',
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'estado_filter'}),
        choices=Reserva.Estado.choices,
    )

    class Meta:
        model = Reserva
        fields = [
            'usuario', 'ubicacion', 'piso',
            'espacio', 'fecha_uso',
            'hora_inicio', 'hora_fin', 'estado',
        ]

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
                Field('usuario', css_class='w-full'),
                css_class='w-full',
            ),
            Row(
                Column('ubicacion', css_class='w-2/3'),
                Column('piso', css_class='w-1/3'),
            ),
            Div(
                Field('espacio', css_class='w-full'),
            ),
            Div(
                Field('fecha_uso', css_class='w-full'),
            ),
            Div(
                Field('estado', css_class='w-full'),
            ),
            Row(
                Column('hora_inicio', css_class='w-1/2 pr-1'),
                Column('hora_fin', css_class='w-1/2 pl-1'),
            ),
            Submit('submit', 'Filtrar', css_class='btn btn-primary w-full mt-4')
        )


class ReservaFilterCards(django_filters.FilterSet):
    fecha_uso = django_filters.DateFilter(
        field_name='fecha_uso',
        lookup_expr='exact',

    )
    
    estado = django_filters.ChoiceFilter(
        field_name='estado',
        lookup_expr='exact',
        choices=Reserva.Estado.choices,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
