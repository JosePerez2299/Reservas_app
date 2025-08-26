from django import forms
from apps.reservas.models import Espacio, Reserva 
from django.utils import timezone

from apps.usuarios.models import Ubicacion
from apps.espacios.models import PlataformaDigital

class EspacioCreateForm(forms.ModelForm):
    # Campos básicos del espacio
    nombre = forms.CharField(label='Nombre del espacio')
    tipo_ubicacion = forms.ChoiceField(
        choices=Espacio.TipoUbicacion.choices,
        widget=forms.RadioSelect,
        label='Tipo de Espacio',
        initial=Espacio.TipoUbicacion.FISICO
    )
    tipo = forms.ChoiceField(choices=Espacio.Tipo.choices, label='Tipo de espacio', required=False)
    disponible = forms.BooleanField(required=False, initial=True, label='Disponible')
    descripcion = forms.CharField(widget=forms.Textarea, label='Descripción')
    piso = forms.IntegerField(min_value=0, max_value=40, label='Piso')
    capacidad_maxima = forms.IntegerField(min_value=1, max_value=1000, label='Capacidad máxima')

    # Campos para espacios físicos
    ubicacion = forms.ModelChoiceField(
        queryset=Ubicacion.objects.all() , 
        label='Ubicación física', 
        required=False
    )

    # Campos para espacios digitales
    plataforma = forms.ModelChoiceField(
        queryset=PlataformaDigital.objects.all(), 
        label='Plataforma digital', 
        required=False
    )

   
    class Meta:
        model = Espacio
        fields = ['nombre', 'piso', 'capacidad_maxima', 'tipo_ubicacion', 'tipo', 'disponible', 'descripcion']


    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.initial_disponible = self.instance.disponible if self.instance.pk else True

class EspacioUpdateForm(forms.ModelForm):
    pass


# class EspacioUpdateForm(EspacioCreateForm):

#     def save(self, commit=True):
#         espacio = super().save(commit=False)
            
#         # Solo procesar si realmente cambió la disponibilidad de True a False
#         if (self.initial_disponible and 
#             not self.cleaned_data.get('disponible', True)):
            
#             # Obtener reservas futuras pendientes y aprobadas
#             reservas_afectadas = Reserva.objects.filter(
#                 fecha_uso__gte=timezone.now().date(),
#                 espacio=espacio.id,
#                 estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA]
#             )
            
#             # Actualizar cada reserva individualmente para que se registre en audit log
#             for reserva in reservas_afectadas:
#                 reserva.estado = Reserva.Estado.RECHAZADA
#                 reserva.aprobado_por = self.request.user
#                 reserva.motivo_admin = 'El espacio no se encuentra disponible'
#                 reserva.save()  
            
#         if commit:
#             espacio.save()
            
#         return espacio