import django_filters
from reservas.models import Reserva, Espacio, Ubicacion
from django import forms
class ReservaFilter(django_filters.FilterSet):
    usuario = django_filters.CharFilter(
        field_name='usuario__username',
        lookup_expr='icontains',
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre de usuario...', 'id': 'username_filter'})
    )

    espacio = django_filters.CharFilter(
        field_name='espacio__nombre',
        lookup_expr='icontains',
        label='Espacio',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre de espacio...', 'id': 'espacio_filter'})

    )   
    
    fecha_uso = django_filters.DateFilter(
        field_name='fecha_uso',
        lookup_expr='exact',
        label='Fecha de uso',
        widget=forms.DateInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary transition-colors duration-200',
            'type': 'date'
        })
    )
    
    hora_inicio = django_filters.TimeFilter(
        field_name='hora_inicio',
        lookup_expr='gte',
        label='Hora de inicio',
        widget=forms.TimeInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary transition-colors duration-200',
            'type': 'time'
        })
    )
    hora_fin = django_filters.TimeFilter(
        field_name='hora_fin',
        lookup_expr='lte',
        label='Hora de fin',
        widget=forms.TimeInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary transition-colors duration-200',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
