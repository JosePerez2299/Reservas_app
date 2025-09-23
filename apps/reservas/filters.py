import django_filters
from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from django import forms


class ReservaFilter(django_filters.FilterSet):
    nombre_solicitante = django_filters.CharFilter(
        field_name='nombre_solicitante',
        lookup_expr='icontains',
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Buscar por nombre de usuario…',
            'id': 'username_filter'
        })
    )
    p00_solicitante = django_filters.CharFilter(
        field_name='p00_solicitante',
        lookup_expr='icontains',
        label='P00 solicitante',
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Buscar por P00 solicitante…',
            'id': 'p00_filter'
        })
    )

    espacios = django_filters.ModelChoiceFilter(
        queryset=Espacio.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2 input w-full'
        }),
        required=False,
        label='Espacio',
        method='filter_by_espacio'
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
            attrs={'type': 'time', 'fieldset_class': 'w-1/2 flex-1', 'class': 'input'}),
    )

    hora_fin = django_filters.TimeFilter(
        field_name='hora_fin',
        lookup_expr='lte',
        label='Hora de fin',
        widget=forms.TimeInput(
            attrs={'type': 'time', 'fieldset_class': 'w-1/2 ', 'class': 'input'}),

    )

    modalidad = django_filters.ChoiceFilter(
        field_name='modalidad',
        label='Modalidad',
        widget=forms.Select(
            attrs={'class': 'select', 'id': 'modalidad_filter'}),
        choices=Reserva.Modalidad.choices,
    )

    tipo_solicitud = django_filters.ChoiceFilter(
        field_name='tipo_solicitud',
        label='Tipo de solicitud',
        widget=forms.Select(
            attrs={'class': 'select', 'id': 'tipo_solicitud_filter'}),
        choices=Reserva.TipoSolicitud.choices,
    )
    estado = django_filters.ChoiceFilter(
        field_name='estado',
        lookup_expr='icontains',
        label='Estado',
        widget=forms.Select(
            attrs={'class': 'select', 'id': 'estado_filter'}),
        choices=Reserva.Estado.choices,
    )

    ordering = django_filters.OrderingFilter(
        label='Ordenar por',
        fields=(
            ('id', 'id'),
            ('p00_solicitante', 'p00_solicitante'),
            ('nombre_solicitante', 'nombre_solicitante'),
            ('modalidad', 'modalidad'),
            ('fecha_uso', 'fecha_uso'),
            ('estado', 'estado'),
            ('aprobado_por__username', 'aprobado_por'),
        ),
        field_labels={
            'id': 'ID',
            'nombre': 'Nombre',
            'modalidad': 'Modalidad',
            'capacidad_maxima': 'Capacidad',
            'ubicacion': 'Ubicación',
            'disponible': 'Disponible',
        },
    )

    class Meta:
        model = Reserva
        fields = [
            'nombre_solicitante',
            'p00_solicitante',
            'modalidad',
            'tipo_solicitud',
            'espacios', 
            'fecha_uso',
            'hora_inicio', 
            'hora_fin', ''
            'estado',
        ]

    def filter_by_espacio(self, queryset, name, value):
        if value:
            return queryset.filter(espacios=value)
        return queryset


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
