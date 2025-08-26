from django import forms
from apps.reservas.models import Espacio, Reserva 
from django.utils import timezone
from django.db import transaction

from apps.usuarios.models import Ubicacion
from apps.espacios.models import DetalleEspacioFisico, DetalleEspacioDigital, PlataformaDigital

class EspacioCreateForm(forms.ModelForm):
    # Campos básicos del espacio
    nombre = forms.CharField(label='Nombre del espacio', required=True)
    tipo = forms.ChoiceField(
        required=True,
        choices=Espacio.Tipo.choices,
        widget=forms.RadioSelect,
        label='Tipo de Espacio',
        initial=Espacio.Tipo.FISICO
    )
    disponible = forms.BooleanField(required=True, initial=True, label='Disponible')
    descripcion = forms.CharField(widget=forms.Textarea, label='Descripción', required=True)
    capacidad_maxima = forms.IntegerField(min_value=1, max_value=1000, label='Capacidad máxima', required=True)

    # Campos para espacios físicos
    piso = forms.IntegerField(min_value=0, max_value=40, label='Piso', required=False)
    ubicacion = forms.ModelChoiceField(
        queryset=Ubicacion.objects.all() , 
        label='Ubicación física', 
        required=False
    )
    espacio_tipo = forms.ChoiceField(
        choices=DetalleEspacioFisico.Tipo.choices,
        label='Tipo de espacio',
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
        fields = ['nombre', 'piso', 'capacidad_maxima', 'tipo', 'disponible', 'descripcion', 'espacio_tipo', 'plataforma', 'ubicacion']

    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.initial_disponible = self.instance.disponible if self.instance.pk else True
        

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        if tipo == Espacio.Tipo.FISICO:
            if not cleaned_data.get('ubicacion'):
                self.add_error('ubicacion', 'Este campo es requerido para espacios físicos.')
            if cleaned_data.get('piso') is None:
                self.add_error('piso', 'Este campo es requerido para espacios físicos.')
            if not cleaned_data.get('espacio_tipo'):
                self.add_error('espacio_tipo', 'Este campo es requerido para espacios físicos.')

        elif tipo == Espacio.Tipo.DIGITAL:
            if not cleaned_data.get('plataforma'):
                self.add_error('plataforma', 'Este campo es requerido para espacios digitales.')

        return cleaned_data

    def save(self, commit=True):
        if not commit:
            raise ValueError("EspacioCreateForm.save() requiere commit=True para crear detalles relacionados.")

        with transaction.atomic():
            espacio = super().save(commit=True)
            tipo = self.cleaned_data.get('tipo')

            if tipo == Espacio.Tipo.FISICO:
                DetalleEspacioFisico.objects.create(
                    espacio=espacio,
                    piso=self.cleaned_data.get('piso'),
                    tipo=self.cleaned_data.get('espacio_tipo'),
                    ubicacion=self.cleaned_data.get('ubicacion'),
                )
            elif tipo == Espacio.Tipo.DIGITAL:
                DetalleEspacioDigital.objects.create(
                    espacio=espacio,
                    plataforma=self.cleaned_data.get('plataforma'),
                )

            return espacio

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