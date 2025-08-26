from django import forms
from apps.reservas.models import Espacio, Reserva 
from django.utils import timezone

class EspacioCreateForm(forms.ModelForm):
    nombre = forms.CharField()
    class Meta:
        model = Espacio
        fields = ['nombre']

      
        help_texts = {

            'nombre': 'Nombre del espacio',
           
        }


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