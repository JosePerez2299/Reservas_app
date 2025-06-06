# forms.py
from django import forms
from reservas.models import Espacio, Reserva 
from django.utils import timezone
from django_select2.forms import Select2Widget

class EspacioCreateForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo', 'disponible']
        widgets = {
            'ubicacion': Select2Widget,
        }


class EspacioUpdateForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo', 'disponible']
        widgets = {
            'ubicacion': Select2Widget,

        }
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        # Guardamos el estado inicial de disponibilidad
        self.initial_disponible = self.instance.disponible if self.instance.pk else True
    
    def save(self, commit=True):
        espacio = super().save(commit=False)

            
        # Solo procesar si realmente cambió la disponibilidad de True a False
        if (self.initial_disponible and 
            not self.cleaned_data.get('disponible', True)):
            
            # Filtrar reservas futuras pendientes y aprobadas
            reserva_qs = Reserva.objects.filter(
                fecha_uso__gte=timezone.now().date(),
                espacio=espacio.id,
                estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA]
            )
            
            # Opcional: Guardar información de las reservas afectadas para notificaciones
            reservas_afectadas = list(reserva_qs.values_list('id', flat=True))
            
            # Rechazar las reservas
            reservas_actualizadas = reserva_qs.update(estado='rechazada', aprobado_por=self.request.user, motivo_admin='El espacio no se encuentra disponible')
            
            # Log o mensaje informativo (opcional)
            if reservas_actualizadas > 0:
                # Aquí podrías agregar logging o envío de notificaciones
                print(f"Se rechazaron {reservas_actualizadas} reservas debido a la indisponibilidad del espacio {espacio.nombre}")
        
        if commit:
            espacio.save()
            
        return espacio