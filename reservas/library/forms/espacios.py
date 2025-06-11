from django import forms
from reservas.models import Espacio, Reserva 
from django.utils import timezone
from django_select2.forms import Select2Widget

class EspacioCreateForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo', 'descripcion', 'disponible']
        widgets = {
            'ubicacion': Select2Widget,
        }


class EspacioUpdateForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo', 'descripcion', 'disponible']
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
            
            # Obtener reservas futuras pendientes y aprobadas
            reservas_afectadas = Reserva.objects.filter(
                fecha_uso__gte=timezone.now().date(),
                espacio=espacio.id,
                estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA]
            )
            
            # Actualizar cada reserva individualmente para que se registre en audit log
            for reserva in reservas_afectadas:
                reserva.estado = Reserva.Estado.RECHAZADA
                reserva.aprobado_por = self.request.user
                reserva.motivo_admin = 'El espacio no se encuentra disponible'
                reserva.save()  # Esto triggerea las señales y el audit log
            
        if commit:
            espacio.save()
            
        return espacio