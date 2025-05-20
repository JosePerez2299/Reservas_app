import django_filters
from reservas.models import Espacio

class EspacioFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(
        field_name='nombre',
        lookup_expr='icontains',
        label='Nombre',
        widget=django_filters.widgets.forms.TextInput(attrs={
            'class': 'w-full text-sm bg-gray-600 text-white border-gray-500 rounded px-2 py-1',
            'placeholder': 'Buscar por nombre...'
        })
    )
    
    capacidad_min = django_filters.NumberFilter(
        field_name='capacidad',
        lookup_expr='gte',
        label='Capacidad mínima',
        widget=django_filters.widgets.forms.NumberInput(attrs={
            'class': 'w-full text-sm bg-gray-600 text-white border-gray-500 rounded px-2 py-1',
            'placeholder': 'Mínimo',
            'min': '1'
        })
    )
    
    capacidad_max = django_filters.NumberFilter(
        field_name='capacidad',
        lookup_expr='lte',
        label='Capacidad máxima',
        widget=django_filters.widgets.forms.NumberInput(attrs={
            'class': 'w-full text-sm bg-gray-600 text-white border-gray-500 rounded px-2 py-1',
            'placeholder': 'Máximo',
            'min': '1'
        })
    )
    
    piso = django_filters.NumberFilter(
        field_name='piso',
        lookup_expr='exact',
        label='Piso',
        widget=django_filters.widgets.forms.NumberInput(attrs={
            'class': 'w-full text-sm bg-gray-600 text-white border-gray-500 rounded px-2 py-1',
            'placeholder': 'Número de piso',
            'min': '0'
        })
    )
    
    disponible = django_filters.BooleanFilter(
        field_name='disponible',
        label='Disponible',
        widget=django_filters.widgets.forms.CheckboxInput(attrs={
            'class': 'rounded text-blue-600 focus:ring-blue-500',
        })
    )
    
    class Meta:
        model = Espacio
        fields = ['tipo']  # El campo tipo se manejará por defecto

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar el widget para el campo tipo
        self.filters['tipo'].field.widget.attrs.update({
            'class': 'w-full text-sm bg-gray-600 text-white border-gray-500 rounded px-2 py-1',
        })
