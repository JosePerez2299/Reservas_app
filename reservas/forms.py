from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationForm(UserCreationForm):
    error_css_class = 'error'
    required_css_class = 'required'
    label_suffix = ':'

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        error_messages = {
            'username': {
                'required': 'Este campo es obligatorio.',
                'unique': 'Este nombre de usuario ya está en uso.',
            },
            'email': {
                'required': 'Este campo es obligatorio.',
                'invalid': 'Introduce una dirección de correo electrónico válida.',
            },
            'password1': {
                'required': 'Este campo es obligatorio.',
            },
            'password2': {
                'required': 'Este campo es obligatorio.',
            },
        }

