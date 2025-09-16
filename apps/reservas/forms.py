from datetime import timedelta
from django.urls import reverse
from apps.espacios.models import Espacio
from apps.reservas.models import DetalleReservaDigital, Reserva, TipoActividad, ReservaEspacio
from apps.usuarios.models import Usuario

from django import forms
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.db.models import Q

# Step1: Contacto
class ContactoForm(forms.ModelForm):
    p00_solicitante = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input ", "readonly": True}),
        help_text="P00 del  usuario",
    )

    nombre_solicitante = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "input ",
                "placeholder": "Nombre del solicitante",
                "readonly": True,
            }
        ),
        help_text="Nombre del solicitante",
    )

    email_solicitante = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "input ",
                "placeholder": "Email del solicitante",
                "readonly": True,
            }
        ),
        help_text="Email del solicitante",
    )

    telefono_solicitante = PhoneNumberField(
        widget=forms.TextInput(attrs={
            'type': 'tel',
            'placeholder': '+58 414 123 4567',
            'class': 'input w-full'
        }),
        error_messages={
            'invalid': 'Por favor, ingrese un número de teléfono válido.',
        },
        help_text="Este campo es editable, debe tener el formato +58 414 123 4567",
        
        label='Número de Celular',
        region='VE'  
    )

    vicepresidencia_solicitante = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "input ",
                "placeholder": "Vicepresidencia del solicitante",
                "readonly": True,
            }
        ),
        required=False,
        help_text="Vicepresidencia del solicitante",
    )

    gerencia_solicitante = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "input ",
                "placeholder": "Gerencia del solicitante",
                "readonly": True,
            }

        ),
        required=False,
        help_text="Gerencia del solicitante",

    )


    class Meta:
        model = Reserva
        fields = [
            "p00_solicitante",
            "nombre_solicitante",
            "email_solicitante",
            "telefono_solicitante",
            "vicepresidencia_solicitante",
            "gerencia_solicitante",]


# Step2: Reserva
class ReservaForm(forms.ModelForm):
    modalidad = forms.ChoiceField(
        choices=Reserva.Modalidad.choices,
        help_text="Indica la modalidad de la reserva (presencial o virtual)",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )

    tipo_solicitud = forms.ChoiceField(
        choices=Reserva.TipoSolicitud.choices,
        help_text="Indica el tipo de solicitud de la reserva",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )

    fecha_uso = forms.DateField(
        help_text="Indica la fecha de uso de la reserva",
        widget=forms.DateInput(attrs={"class": "input w-full", "type": "date", "min": timezone.now().date(), "max": timezone.now().date() + timedelta(days=30)}),
    )

    tipo_actividad = forms.ModelChoiceField(
        queryset=TipoActividad.objects.all(),
        help_text="Indica el tipo de actividad que se realizará en el espacio, si no existe, selecionar 'otro'",
        widget=forms.Select(attrs={"class": "select2 w-full"}),
    )

    motivo = forms.CharField(
        help_text="Indica el motivo de la reserva",
        widget=forms.Textarea(attrs={"class": "w-full textarea textarea-bordered"}),
    )

    hora_inicio = forms.TimeField(
        help_text="Indica la hora de inicio de la reserva",
        widget=forms.TimeInput(
            attrs={"class": "input w-full", "type": "time", "min": "09:00", "max": "20:00", "step": "900"},
        )
    )

    hora_fin = forms.TimeField(
        help_text="Indica la hora de fin de la reserva",
        widget=forms.TimeInput(
            attrs={"class": "input w-full", "type": "time", "min": "09:00", "max": "20:00", "step": "900"},
        )
    )

    class Meta:
        model = Reserva
        fields = [
            "tipo_solicitud",
            "modalidad",
            "tipo_actividad",
            "fecha_uso",
            "hora_inicio",
            "hora_fin",
            "motivo",
        ]

#Step3: Requerimiento (Solo presencial o mixta)
class RequerimientoForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["requerimientos" , "observacion"]


#Step4: Espacio Presencial (Solo presencial o mixta)
class ReservaEspacioFisicoForm(forms.ModelForm):
    class Meta:
        model = ReservaEspacio
        fields = ["espacio", "numero_participantes"]
    
    def __init__(self, *args, **kwargs):
        # Recibimos la reserva desde el wizard
        self.reserva = kwargs.pop('reserva', None)
        super().__init__(*args, **kwargs)
        self.fields['espacio'].queryset = Espacio.objects.filter(tipo=Espacio.Tipo.FISICO, disponible=True)
    
    def clean(self):
        cleaned_data = super().clean()
        espacio = cleaned_data.get('espacio')
        
        # Si no tenemos el objeto reserva o el espacio, no podemos validar
        if not self.reserva or not espacio:
            return cleaned_data
            
        # Buscar reservas aprobadas del mismo espacio en la misma fecha que se solapan con el horario
        reservas_solapadas = ReservaEspacio.objects.filter(
            espacio=espacio,
            reserva__fecha_uso=self.reserva.fecha_uso,
            reserva__estado=Reserva.Estado.APROBADA
        ).filter(
            # Condición para detectar solapamiento de horarios:
            # (hora_inicio < hora_fin_nueva) AND (hora_fin > hora_inicio_nueva)
            Q(reserva__hora_inicio__lt=self.reserva.hora_fin) &
            Q(reserva__hora_fin__gt=self.reserva.hora_inicio)
        )
        
        if reservas_solapadas.exists():
            raise ValidationError(
                "Ya existe una reserva aprobada para este espacio en la fecha y horario seleccionados."
            )
            
        if self.cleaned_data['numero_participantes'] > espacio.capacidad_maxima:
            raise ValidationError(
                "El número de participantes supera la capacidad del espacio. Capacidad máxima: {}".format(espacio.capacidad_maxima)
            )
        return cleaned_data
            

    
#Step5: Espacio Virtual (Solo virtual o mixta)
class ReservaEspacioDigitalForm(forms.ModelForm):
    class Meta:
        model = ReservaEspacio
        fields = ["espacio", "numero_participantes"]
    
    def __init__(self, *args, **kwargs):
        # Recibimos la reserva desde el wizard
        self.reserva = kwargs.pop('reserva', None)
        super().__init__(*args, **kwargs)
        self.fields['espacio'].queryset = Espacio.objects.filter(tipo=Espacio.Tipo.DIGITAL, disponible=True)
        
    def clean(self):
        cleaned_data = super().clean()
        espacio = cleaned_data.get('espacio')
        
        # Si no tenemos el objeto reserva o el espacio, no podemos validar
        if not self.reserva or not espacio:
            return cleaned_data
            
        # Buscar reservas aprobadas del mismo espacio en la misma fecha que se solapan con el horario
        reservas_solapadas = ReservaEspacio.objects.filter(
            espacio=espacio,
            reserva__fecha_uso=self.reserva.fecha_uso,
            reserva__estado=Reserva.Estado.APROBADA
        ).filter(
            # Condición para detectar solapamiento de horarios:
            # (hora_inicio < hora_fin_nueva) AND (hora_fin > hora_inicio_nueva)
            Q(reserva__hora_inicio__lt=self.reserva.hora_fin) &
            Q(reserva__hora_fin__gt=self.reserva.hora_inicio)
        )
        
        if reservas_solapadas.exists():
            raise ValidationError(
                "Ya existe una reserva aprobada para este espacio en la fecha y horario seleccionados."
            )

        if self.cleaned_data['numero_participantes'] > espacio.capacidad_maxima:
            raise ValidationError(
                "El número de participantes supera la capacidad del espacio. Capacidad máxima: {}".format(espacio.capacidad_maxima)
            )
            
        return cleaned_data

class DetalleReservaDigitalForm(forms.ModelForm):
    class Meta:
        model = DetalleReservaDigital
        fields = ["anfitrion_usuario", "ubicacion_transmision", "espacio_transmision"]

# Modelo Reserva:
# Requerimientos y observacion adicionales.

# Modelo ReservaEspacio:
# Numero de participantes y seleccion de espacios (mostrar sede, y despues los espacios de esa sede).
# Crear el form para cada uno, si es mixta, hacer doble insert, ejecutar cada step.






class ReservaCreateForm(forms.ModelForm):
    espacio = forms.ModelChoiceField(
        queryset=Espacio.objects.all(),
        widget=forms.Select(attrs={"class": "select select-bordered"}),
    )
    fecha_uso = forms.DateField(
        widget=forms.DateInput(attrs={"class": "date-input", "type": "date"})
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={"class": "time-input", "type": "time"})
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={"class": "time-input", "type": "time"})
    )

    class Meta:
        model = Reserva
        fields = [
            "p00_solicitante",
            "espacio",
            "fecha_uso",
            "hora_inicio",
            "hora_fin",
            "motivo",
        ]


class DetalleReservaDigitalForm(forms.ModelForm):
    class Meta:
        model = DetalleReservaDigital
        fields = ["anfitrion_usuario", "ubicacion_transmision", "espacio_transmision"]


class ReservaApproveForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ["estado", "mensaje_aprobar_rechazar"]
