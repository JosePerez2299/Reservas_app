from django import forms
from apps.reservas.models import Espacio, Reserva 
from django.utils import timezone
from django.db import transaction

from apps.usuarios.models import Ubicacion
from apps.espacios.models import DetalleEspacioFisico, DetalleEspacioDigital, PlataformaDigital

class EspacioForm(forms.ModelForm):
    tipo = forms.ChoiceField(choices=Espacio.Tipo.choices, widget=forms.RadioSelect, initial=Espacio.Tipo.FISICO)
    class Meta:
        model = Espacio
        fields = ['nombre','capacidad_maxima','tipo','descripcion','disponible',]

class DetalleDigitalForm(forms.ModelForm):
    class Meta:
        model = DetalleEspacioDigital
        fields = ['plataforma']


class DetalleFisicoForm(forms.ModelForm):
    class Meta:
        model = DetalleEspacioFisico
        fields = ['piso','tipo','ubicacion']




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