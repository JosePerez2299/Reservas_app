# forms.py
from django import forms
from reservas.models import Espacio 

class EspacioCreateForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = '__all__'  # Puedes usar una lista si solo quieres algunos campos
