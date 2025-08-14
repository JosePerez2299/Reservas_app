from django.db import models
from django.core.exceptions import ValidationError
import re
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.admin.models import LogEntry
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Q


# ——— 1. Ubicación —————————————————————————————————————————————
class Ubicacion(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Ubicaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# ——— 2. Usuario —————————————————————————————————————————————
def validate_username(value):
    """
    Validador personalizado para username:
    - Mínimo 3 caracteres
    - Máximo 20 caracteres  
    - No puede comenzar con número o carácter especial
    - Solo permite letras, números y guiones bajos
    """
    # Verificar longitud mínima
    if len(value) < 3:
        raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
    
    # Verificar longitud máxima
    if len(value) > 20:
        raise ValidationError('El nombre de usuario no puede exceder 20 caracteres.')
    
    # Verificar que no comience con número o carácter especial
    if not value[0].isalpha():
        raise ValidationError('El nombre de usuario debe comenzar con una letra.')
    
    # Verificar que solo contenga caracteres permitidos (letras, números, guiones bajos)
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', value):
        raise ValidationError(
            'El nombre de usuario solo puede contener letras, números y guiones bajos, '
            'y debe comenzar con una letra.'
        )

class Usuario(AbstractUser):
    """
    Modelo personalizado para usuarios
    """
    GRUPOS = settings.GRUPOS

    username = models.CharField(
        'Nombre de usuario',
        max_length=20,
        unique=True,
        validators=[validate_username],
        help_text='Nombre de usuario único. 3-20 caracteres. Debe comenzar con letra.',
        error_messages={
            'unique': "Ya existe un Usuario con este nombre.",
        },  
    )
    
    email = models.EmailField(unique=True)
    ubicacion = models.ForeignKey(

        'Ubicacion', on_delete=models.SET_NULL, 
        null=True,
        help_text="La sede/edificio al que pertenece el usuario", 
    )
    piso = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="Piso en el que puede moderar o reservar"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']


    def __str__(self):
        return self.username

    @property
    def is_moderador(self):
        return self.groups.filter(name=self.GRUPOS.MODERADOR).exists()

    @property
    def is_usuario(self):
        return self.groups.filter(name=self.GRUPOS.USUARIO).exists()

    @property
    def is_admin(self):
        return self.groups.filter(name=self.GRUPOS.ADMINISTRADOR).exists()

    @property
    def grupo(self):
        return self.groups.first().name if self.groups.exists() else self.GRUPOS.USUARIO
