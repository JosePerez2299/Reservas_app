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
        help_text="Seleccione el tipo de espacio, físico o digital",
    )
    disponible = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Indica si el espacio está disponible",
        widget=forms.CheckboxInput(attrs={"class": "toggle toggle-success toggle-xl"}),
    )
    capacidad_maxima = forms.IntegerField(
        required=True,
        help_text="Cantidad máxima de personas",
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
        fields = ["plataforma", "url"]


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
        help_text="Seleccione el tipo de espacio, físico o digital",
    )

    foto = forms.ImageField(
        required=True,
        help_text="Seleccione la foto del espacio",
        widget=forms.FileInput(attrs={}),
    )

    class Meta:
        model = DetalleEspacioFisico
        fields = ["piso", "tipo", "ubicacion", "foto"]

# Formulario vacío para el paso de resumen
class EmptyForm(forms.Form):
    pass
