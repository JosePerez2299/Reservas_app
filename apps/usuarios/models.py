from django.db import models
from django.core.exceptions import ValidationError
import re
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.contrib.auth.models import AbstractUser

def validate_username(value):
    """
    Validador para username:
    - 3 a 20 caracteres
    - comienza con letra
    - solo letras, números y guión bajo
    """
    pattern = r'^[A-Za-z][A-Za-z0-9_]{2,19}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'El nombre de usuario debe tener entre 3 y 20 caracteres, '
            'comenzar con una letra y solo puede contener letras, números y guiones bajos.'
        )

class Usuario(AbstractUser):
    """
    Modelo personalizado para usuarios.
    Asegúrate de tener AUTH_USER_MODEL = 'tuapp.Usuario' en settings.py
    antes de crear las migraciones iniciales.
    """
    GRUPOS = getattr(settings, 'GRUPOS', None)

    username = models.CharField(
        'Nombre de usuario',
        max_length=20,
        unique=True,
        validators=[validate_username],
        help_text='Nombre de usuario único. 3-20 caracteres. Debe comenzar con letra.',
        error_messages={'unique': "Ya existe un Usuario con este nombre."},
    )
    
    p00 = models.CharField(
        'P00',
        max_length=8,
        unique=True,
        help_text='Código P00 único del usuario (8 caracteres).',
    )

    email = models.EmailField(unique=True)

    telefono = models.CharField(max_length=100)

    vicepresidencia = models.CharField('Vicepresidencia', max_length=6, blank=True, help_text='Vicepresidencia del usuario')
    
    gerencia = models.CharField('Gerencia', max_length=6, blank=True, help_text='Gerencia del usuario')

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']

    def __str__(self):
        return self.username

    # Utilidad general para comprobar pertenencia a grupo
    def has_group(self, group_name):
        return self.groups.filter(name=group_name).exists()

    @property
    def is_admin(self):
        if not self.GRUPOS:
            return self.has_group('Administrador')
        return self.has_group(self.GRUPOS.ADMINISTRADOR)

    @property
    def is_usuario(self):
        if not self.GRUPOS:
            return self.has_group('Usuario')
        return self.has_group(self.GRUPOS.USUARIO)

    @property
    def grupo(self):
        """
        Devuelve el primer grupo del usuario (si existe) o el grupo por defecto.
        """
        if self.groups.exists():
            return self.groups.first().name
        if hasattr(self.GRUPOS, 'USUARIO'):
            return self.GRUPOS.USUARIO
        return 'usuario'
