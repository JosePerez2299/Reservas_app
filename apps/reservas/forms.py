from django.urls import reverse
from apps.espacios.models import Espacio
from apps.reservas.models import DetalleReservaDigital, Reserva, TipoActividad
from apps.usuarios.models import Usuario

from django import forms


# Selecciona el usuario que va a realizar la reserva
class ContactoForm(forms.ModelForm):
    p00_solicitante = forms.CharField(
        widget=forms.TextInput(attrs={"class": "input ", "readonly": True})
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
    )

    email_solicitante = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "input ",
                "placeholder": "Email del solicitante",
                "readonly": True,
            }
        )
    )

    telefono_solicitante = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "input ", "placeholder": "Teléfono del solicitante"}
        ),
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


class ReservaForm(forms.ModelForm):
    modalidad = forms.ChoiceField(
        choices=Reserva.Modalidad.choices,
        widget=forms.Select(attrs={"class": "select select-bordered"}),
    )

    tipo_solicitud = forms.ChoiceField(
        choices=Reserva.TipoSolicitud.choices,
        widget=forms.Select(attrs={"class": "select select-bordered"}),
    )

    fecha_uso = forms.DateField(
        widget=forms.DateInput(attrs={"class": "input", "type": "date"})
    )

    tipo_actividad = forms.ModelChoiceField(
        queryset=TipoActividad.objects.all(),
        widget=forms.Select(attrs={"class": "select select-bordered"}),
    )

    motivo = forms.CharField(
        widget=forms.Textarea(attrs={"class": "textarea textarea-bordered"}),
    )

    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={"class": "input", "type": "time"})
    )

    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={"class": "input", "type": "time"})
    )

    observacion = forms.CharField(
        widget=forms.Textarea(attrs={"class": "textarea textarea-bordered"}),
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
            "observacion",
        ]


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
