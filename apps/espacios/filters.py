import django_filters
from django import forms

class EspacioFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        field_name='nombre',
        lookup_expr='icontains',
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Buscar por nombre...', 'id': 'nombre_filter'})

    )

    tipo = django_filters.ChoiceFilter(
        field_name='tipo',
        choices=[
            ('fisico', 'Físico'),
            ('digital', 'Digital'),
        ],
        widget=forms.Select(attrs={'class': 'select', 'id': 'tipo_filter'})
    )
    
    capacidad_min = django_filters.NumberFilter(
        field_name='capacidad_maxima',
        lookup_expr='gte',
        label='Capacidad mínima',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por capacidad mínima...', 'id': 'capacidad_min_filter'})

    )
    
    capacidad_max = django_filters.NumberFilter(
        field_name='capacidad_maxima',
        lookup_expr='lte',
        label='Capacidad máxima',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por capacidad máxima...', 'id': 'capacidad_max_filter'})

    )
    

    disponible = django_filters.ChoiceFilter(
        field_name='disponible',
        choices=[
            ('True', 'Sí'),
            ('False', 'No'),
        ],
        widget=forms.Select(attrs={'class': 'select', 'id': 'disponible_filter'}),  
        label='Disponible',
    )

    ordering = django_filters.OrderingFilter(
        
        fields=(
            ('id', 'id'),
            ('nombre', 'nombre'),
            ('tipo', 'tipo'),
            ('capacidad_maxima', 'capacidad_maxima'),
            ('ubicacion', 'ubicacion'),
            ('disponible', 'disponible'),
        ),
        field_labels={
            'id': 'ID',
            'nombre': 'Nombre',
            'tipo': 'Tipo', 
            'capacidad_maxima': 'Capacidad',
            'ubicacion': 'Ubicación',
            'disponible': 'Disponible',
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
