import django_filters
from reservas.models import Reserva
from apps.usuarios.models import Ubicacion
from apps.espacios.models import Espacio
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, Field


class ReservaFilter(django_filters.FilterSet):
    usuario = django_filters.CharFilter(
        field_name='usuario__username',
        lookup_expr='icontains',
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Buscar por nombre de usuario…',
            'id': 'username_filter'
        })
    )
    ubicacion = django_filters.CharFilter(
        field_name='espacio__ubicacion',
        lookup_expr='icontains',
        label='Ubicación',
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por ubicación…',
            'class': 'input',
            'id': 'ubicacion_filter'
        }),
    )
    piso = django_filters.NumberFilter(
        field_name='espacio__piso',
        lookup_expr='exact',
        label='Piso',
        widget=forms.NumberInput(
            attrs={'class': 'input', 'placeholder': 'Piso del espacio…'})
    )
    espacio = django_filters.CharFilter(
        field_name='espacio__nombre',
        lookup_expr='icontains',
        label='Espacio',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del espacio…'}),
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
        widget=forms.TimeInput(
            attrs={'type': 'time', 'fieldset_class': 'w-1/2 flex-1', 'class': 'form-control'}),
    )

    hora_fin = django_filters.TimeFilter(
        field_name='hora_fin',
        lookup_expr='lte',
        label='Hora de fin',
        widget=forms.TimeInput(
            attrs={'type': 'time', 'fieldset_class': 'w-1/2 ', 'class': 'form-control'}),

    )
    estado = django_filters.ChoiceFilter(
        field_name='estado',
        lookup_expr='icontains',
        label='Estado',
        widget=forms.Select(
            attrs={'class': 'form-select', 'id': 'estado_filter'}),
        choices=Reserva.Estado.choices,
    )

    class Meta:
        model = Reserva
        fields = [
            'usuario', 'ubicacion', 'piso',
            'espacio', 'fecha_uso',
            'hora_inicio', 'hora_fin', 'estado',
        ]


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
