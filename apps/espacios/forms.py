from django import forms
from apps.core.models import Ubicacion
from apps.espacios.models import Espacio
from apps.espacios.models import DetalleEspacioFisico, DetalleEspacioDigital


class EspacioForm(forms.ModelForm):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Ingrese el nombre del espacio"}),
        required=True,
        help_text="El nombre del espacio",
    )
    tipo = forms.ChoiceField(
        choices=Espacio.Tipo.choices,
        widget=forms.Select(attrs={"class": "select select-bordered"}),
        initial=Espacio.Tipo.FISICO,
        required=True,
        help_text="El tipo de espacio",
    )
    disponible = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Indica si el espacio está disponible",
        widget=forms.CheckboxInput(attrs={"class": "toggle toggle-success toggle-xl"}),
    )
    capacidad_maxima = forms.IntegerField(
        required=True,
        help_text="La capacidad máxima del espacio",
        widget=forms.NumberInput(attrs={"min": 1, "max": 5000, "placeholder": "Ingrese la capacidad máxima del espacio"}),
    )
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "maxlength": 250, "placeholder": "Ingrese la descripción del espacio", "class": "textarea textarea-bordered"}),
        help_text="La descripción del espacio",
    )

    class Meta:
        model = Espacio
        fields = [
            "nombre",
            "capacidad_maxima",
            "tipo",
            "descripcion",
            "disponible",
        ]


class DetalleDigitalForm(forms.ModelForm):
    class Meta:
        model = DetalleEspacioDigital
        fields = ["plataforma"]


class DetalleFisicoForm(forms.ModelForm):
    ubicacion = forms.ModelChoiceField(
        queryset=Ubicacion.objects.all(),
        widget=forms.Select,
        required=True,
        help_text="El edificio en el que se encuentra el espacio",
    )

    piso = forms.IntegerField(
        required=True,
        help_text="En que piso se encuentra el espacio",
        widget=forms.NumberInput(attrs={"min": 1, "max": 50, "placeholder": "Ingrese el piso del espacio"}),
    )
    tipo = forms.ChoiceField(
        choices=DetalleEspacioFisico.Tipo.choices,
        widget=forms.Select(attrs={"class": "select "}),
        required=True,
        help_text="El tipo de espacio",
    )

    class Meta:
        model = DetalleEspacioFisico
        fields = ["piso", "tipo", "ubicacion"]

# Formulario vacío para el paso de resumen
class EmptyForm(forms.Form):
    pass

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
