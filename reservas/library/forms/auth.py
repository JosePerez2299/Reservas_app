from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

User = get_user_model()

class LoginForm(AuthenticationForm):
    """
    Formulario de autenticación de usuarios.
    Hereda de AuthenticationForm de Django y añade estilos y mensajes personalizados.
    """
    username = forms.CharField(
        label=_('Nombre de usuario'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ingrese su nombre de usuario o correo electrónico'),
            'autofocus': True
        }),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )
    
    password = forms.CharField(
        label=_('Contraseña'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ingrese su contraseña'),
            'autocomplete': 'current-password'
        }),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )
    
    error_messages = {
        'invalid_login': _(
            "Por favor ingrese un %(username)s y contraseña correctos. "
            "Note que ambos campos pueden ser sensibles a mayúsculas y minúsculas."
        ),
        'inactive': _("Esta cuenta está inactiva."),
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que los mensajes de error se muestren correctamente
        for field_name, field in self.fields.items():
            field.error_messages = {
                'required': _('Este campo es obligatorio.'),
                **getattr(field, 'error_messages', {})
            }
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
    
    def confirm_login_allowed(self, user):
        """
        Controla si el usuario puede iniciar sesión.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        super().confirm_login_allowed(user)

