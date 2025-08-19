from django import forms
from apps.reservas.models import Espacio, Reserva 
from django.utils import timezone

class EspacioCreateForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo', 'descripcion', 'disponible']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control w-full', 'placeholder': 'Nombre del espacio'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control w-full', 'placeholder': 'Ubicación del espacio'}),
            'piso': forms.NumberInput(attrs={'class': 'form-control w-full', 'placeholder': 'Piso del espacio'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control w-full', 'placeholder': 'Capacidad del espacio'}),
            'tipo': forms.Select(attrs={'class': 'form-select w-full'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción del espacio', 'class': 'form-textarea'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {

            'tipo': 'Tipo de espacio',
           
        }


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.initial_disponible = self.instance.disponible if self.instance.pk else True




class EspacioUpdateForm(EspacioCreateForm):

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
                reserva.save()  
            
        if commit:
            espacio.save()
            
        return espacio