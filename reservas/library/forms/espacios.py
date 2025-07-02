from django import forms
from reservas.models import Espacio, Reserva 
from django.utils import timezone
from django_select2.forms import Select2Widget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Field, Submit, Div

class EspacioCreateForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'ubicacion', 'piso', 'capacidad', 'tipo', 'descripcion', 'disponible']

        help_texts = {

            'tipo': 'Tipo de espacio',
           
        }


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.initial_disponible = self.instance.disponible if self.instance.pk else True


          # Helper y layout con Tailwind
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        
        # IMPORTANTE: Desactivar el renderizado automático del form tag
        # ya que lo manejas manualmente en el template
        self.helper.form_tag = False

        self.helper.layout =    Layout(
            Div(
                Field('nombre', placeholder="Nombre del espacio")
                ),
            Div(
                Field('ubicacion'),
                css_class="mb-4"
                ),
            Div(
                Field('piso', placeholder="Piso del espacio"),
                css_class="mb-4"
                ),
            Div(
                Field('capacidad', placeholder="Capacidad del espacio"),
                css_class="mb-4"
                ),
            Div(
                Field('tipo'),
                css_class="mb-4"
                ),
            Div(
                Field('descripcion', placeholder="Descripción del espacioss", template='components/forms/textarea.html'),
                css_class="mb-4 "
                ),
            Div(
                Field('disponible', template='components/forms/checkbox.html'),
                ),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary w-full'),
            
                )
        )



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