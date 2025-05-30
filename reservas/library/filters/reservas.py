import django_filters
from reservas.models import Reserva, Espacio, Ubicacion
from django.forms.widgets import DateInput, TimeInput
class ReservaFilter(django_filters.FilterSet):
    usuario = django_filters.CharFilter(
        field_name='usuario__username',
        lookup_expr='icontains',
        label='Usuario',

    )

    espacio = django_filters.CharFilter(
        field_name='espacio__nombre',
        lookup_expr='icontains',
        label='Espacio',
    )
    
    fecha_uso = django_filters.DateFilter(
        field_name='fecha_uso',
        lookup_expr='exact',
        label='Fecha de uso',
        widget=DateInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary transition-colors duration-200',
            'type': 'date'
        })
    )
    
    hora_inicio = django_filters.TimeFilter(
        field_name='hora_inicio',
        lookup_expr='gte',
        label='Hora de inicio',
        widget=TimeInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary transition-colors duration-200',
            'type': 'time'
        })
    )
    hora_fin = django_filters.TimeFilter(
        field_name='hora_fin',
        lookup_expr='lte',
        label='Hora de fin',
        widget=TimeInput(attrs={
            'class': 'input input-bordered w-full focus:input-primary transition-colors duration-200',
            'type': 'time'
        })
    )
    
    estado = django_filters.ChoiceFilter(
        field_name='estado',
        lookup_expr='icontains',
        label='Estado',
        choices=Reserva.ESTADO_CHOICES,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
