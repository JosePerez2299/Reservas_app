import django_filters
from reservas.models import Espacio, Ubicacion
from django import forms
class EspacioFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        field_name='nombre',
        lookup_expr='icontains',
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre...', 'id': 'nombre_filter'})

    )

    ubicacion = django_filters.ModelChoiceFilter(
        field_name='ubicacion',
        queryset=Ubicacion.objects.all(),
        label='Ubicación',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'ubicacion_filter'})
    )
    
    capacidad_min = django_filters.NumberFilter(
        field_name='capacidad',
        lookup_expr='gte',
        label='Capacidad mínima',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por capacidad mínima...', 'id': 'capacidad_min_filter'})

    )
    
    capacidad_max = django_filters.NumberFilter(
        field_name='capacidad',
        lookup_expr='lte',
        label='Capacidad máxima',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por capacidad máxima...', 'id': 'capacidad_max_filter'})

    )
    
    piso = django_filters.NumberFilter(
        field_name='piso',
        lookup_expr='exact',
        label='Piso',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por piso...', 'id': 'piso_filter'})

    )
    
    disponible = django_filters.ChoiceFilter(
        field_name='disponible',
        choices=[
            ('True', 'Disponible'),
            ('False', 'No disponible'),
        ],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'disponible_filter'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
