from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import password_validation
from django.utils.text import capfirst
from apps.usuarios.models import Usuario
from django.conf import settings


class UsuarioCreateForm(UserCreationForm):
    # Tu formulario de creación original permanece igual
    groups = forms.ModelChoiceField(
        queryset=Group.objects.exclude(name=settings.GRUPOS.ADMINISTRADOR),
        required=False,
        widget=forms.RadioSelect,
        to_field_name='name' ,
        label='Grupo',
        empty_label="Sin grupo asignado",
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1',
                  'password2', 'ubicacion', 'piso', 'groups']
        help_texts = {
            'username': 'Requerido. 20 caracteres o menos. Debe comenzar con letra.',
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = request.user
        self.fields['password1'].help_text = 'Tu contraseña debe tener al menos 8 caracteres y no puede ser completamente numérica.'
        self.fields['password2'].help_text = 'Ingresa la misma contraseña para verificación.'

        # Establecer grupo 'usuario' por defecto al crear un nuevo usuario
        try:
            grupo_usuario = Group.objects.get(name=settings.GRUPOS.USUARIO)
            self.fields['groups'].initial = grupo_usuario
        except Group.DoesNotExist:
            pass

        if not (user and user.is_admin):
            # Si no es admin, ocultar el campo groups y mantener el grupo "usuario" por defecto
            self.fields['groups'].widget = forms.HiddenInput()
            self.fields['groups'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.groups.clear()
            
            # Obtener el nombre del grupo (ya sea del campo o por defecto)
            grupo_nombre = self.cleaned_data.get('groups') or settings.GRUPOS.USUARIO
            
            try:
                grupo = Group.objects.get(name=grupo_nombre)
                user.groups.add(grupo)
            except Group.DoesNotExist:
                raise forms.ValidationError(f"No se encontró el grupo '{grupo_nombre}'.")
        
        return user
    
class UsuarioUpdateForm(forms.ModelForm):
    # Campos opcionales para cambiar la contraseña
    password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput,
        required=False,
        help_text='Deja en blanco si no deseas cambiar la contraseña. Debe tener al menos 8 caracteres y no puede ser completamente numérica.'
    )
    password2 = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput,
        required=False,
        help_text='Ingresa la misma contraseña para verificación.'
    )

    groups = forms.ModelChoiceField(
        queryset=Group.objects.exclude(name=settings.GRUPOS.ADMINISTRADOR),
        required=False,
        widget=forms.RadioSelect,
        to_field_name='name' ,
        label='Grupo',
        empty_label="Sin grupo asignado",
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'ubicacion', 'piso']

        help_texts = {
            'username': 'Requerido. 20 caracteres o menos. Debe comenzar con letra.',
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request  # Guardar request para usarlo en save()

        user = self.request.user
        grupo_usuario = self.instance.groups.first()
        if grupo_usuario not in Group.objects.exclude(name=settings.GRUPOS.ADMINISTRADOR):
            self.fields['groups'].disabled = True
            self.fields['groups'].widget = forms.HiddenInput()
            return

        if grupo_usuario:
            self.fields['groups'].initial = grupo_usuario
        else:
            self.fields['groups'].initial = Group.objects.get(
                name=settings.GRUPOS.USUARIO)

        # Solo mostrar el campo groups si el usuario es admin
        if not (user and user.is_admin):
            self.fields['groups'].widget = forms.HiddenInput()
            self.fields['groups'].required = False

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Solo validar contraseñas si se proporcionó al menos una
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")

            if password1:
                # Validar la nueva contraseña usando los validadores de Django
                try:
                    password_validation.validate_password(
                        password1, self.instance)
                except forms.ValidationError as error:
                    self.add_error('password1', error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # Solo cambiar la contraseña si se proporcionó una nueva
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)

        if commit:
            user.save()
            if self.cleaned_data.get('groups'):
                user.groups.clear()
                user.groups.add(self.cleaned_data['groups'])

        return user
