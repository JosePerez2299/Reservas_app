import django_filters
from django import forms
from reservas.models import Usuario, Ubicacion
from django.contrib.auth.models import Group

class UsuarioFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre de usuario...'})
    )
    
    email = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por correo...'})
    )
    
    ubicacion = django_filters.ModelChoiceFilter(
        queryset=Ubicacion.objects.all(),
        label='Ubicación',
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Todas las ubicaciones'
    )
    
    piso = django_filters.NumberFilter(
        lookup_expr='exact',
        label='Piso',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de piso...',
            'min': 0,
            'max': 40
        })
    )
    
    def filter_by_group(self, queryset, name, value):
        if value == 'usuario':
            return queryset.filter(groups__name='usuario')
        elif value == 'moderador':
            return queryset.filter(groups__name='moderador')
        return queryset
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_admin:
            self.filters['group_name'] = django_filters.ChoiceFilter(
                label='Grupo',
                method=self.filter_by_group,
                choices=[
                    ('usuario', 'Usuario'),
                    ('moderador', 'Moderador'),
                ],
                widget=forms.Select(attrs={'class': 'form-select'}),
                empty_label='Todos los grupos'
            )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'ubicacion', 'piso']
        order_by = ['username']
