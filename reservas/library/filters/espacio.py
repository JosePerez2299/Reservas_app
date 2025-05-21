import django_filters
from reservas.models import Espacio

class EspacioFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        field_name='nombre',
        lookup_expr='icontains',
        label='Nombre',

    )
    
    capacidad_min = django_filters.NumberFilter(
        field_name='capacidad',
        lookup_expr='gte',
        label='Capacidad mínima',

    )
    
    capacidad_max = django_filters.NumberFilter(
        field_name='capacidad',
        lookup_expr='lte',
        label='Capacidad máxima',

    )
    
    piso = django_filters.NumberFilter(
        field_name='piso',
        lookup_expr='exact',
        label='Piso',

    )
    
    disponible = django_filters.BooleanFilter(
        field_name='disponible',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
