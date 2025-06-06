# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.db.models import Q, F
from django.core.validators import RegexValidator
from django.utils.text import capfirst
import re
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# ——— 1. Ubicación —————————————————————————————————————————————
class Ubicacion(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Ubicaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ——— 2. Usuario personalizado ————————————————————————————————————

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

    GRUPOS = settings.GRUPOS

    username = models.CharField(
        'Nombre de usuario',
        max_length=20,
        unique=True,
        validators=[validate_username],
        help_text='Nombre de usuario único. 3-20 caracteres. Debe comenzar con letra.',
        error_messages={
            'unique': "Ya existe un usuario con este nombre.",
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


# ——— 3. Espacio ———————————————————————————————————————————————
class Espacio(models.Model):
    class Tipo(models.TextChoices):
        SALON     = 'salon', 'Salón'
        LABORATORIO = 'laboratorio', 'Laboratorio'
        AUDITORIO   = 'auditorio', 'Auditorio'

    nombre      = models.CharField(max_length=20, unique=True, blank=False,
            validators=[
                RegexValidator(
                   r"^[a-zA-Z][a-zA-Z0-9 ]*",
                    message="El nombre del espacio debe comenzar con una letra o número, y solo puede contener letras, números y espacios."
                )
        ]) 
    ubicacion   = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    piso        = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="Piso en que se encuentra el espacio (≤ 40)"
    )
    capacidad   = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(1000)],
        help_text="Capacidad máxima (≤ 1000)"
    )
    tipo        = models.CharField(max_length=20, choices=Tipo.choices)
    disponible  = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Espacio"
        verbose_name_plural = "Espacios"
        ordering = ['ubicacion', 'piso', 'nombre']
        indexes = [
            models.Index(fields=['ubicacion', 'piso']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(capacidad__lte=1000),
                name='check_capacidad_max_1000'
            ),
        ]

    def __str__(self):
        return f"{self.nombre}" + " - " + self.ubicacion.nombre + " - " + str(self.piso)


# ——— 4. Reserva ————————————————————————————————————————————————
class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA  = 'aprobada',  'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'
    
    usuario      = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='reservas'
    )
    espacio      = models.ForeignKey(
        Espacio, on_delete=models.CASCADE, related_name='reservas'
    )
    fecha_uso    = models.DateField()
    hora_inicio  = models.TimeField()
    hora_fin     = models.TimeField()
    estado       = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.PENDIENTE
    )
    motivo       = models.TextField(
        "Motivo de reserva", null=False, blank=False
    )
    motivo_admin = models.TextField(
        "Mensaje de aprobación/rechazo", null=True, blank=True
    )
    aprobado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reservas_aprobadas'
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['fecha_uso', 'hora_inicio']
        indexes = [
            models.Index(fields=['espacio', 'fecha_uso']),
        ]
        constraints = [
            # Evita que un mismo usuario haga dos reservas el mismo día en el mismo espacio
            models.UniqueConstraint(
                fields=['usuario', 'espacio', 'fecha_uso'],
                name='uniq_usuario_espacio_fecha',
                violation_error_message="Ya existe una reserva para este usuario en este espacio el mismo día."
            ),
            # Asegura hora_inicio < hora_fin
            models.CheckConstraint(
                check=Q(hora_inicio__lt=F('hora_fin')),
                name='check_hora_inicio_menor_fin',
                violation_error_message="La hora de inicio debe ser menor a la hora de fin."
            ),
        ]

    def __str__(self):
        return f"{self.espacio} — {self.fecha_uso} {self.hora_inicio}-{self.hora_fin}"

    def clean(self):
        super().clean()

        # 1) fecha en el futuro o hoy
        if self.fecha_uso < timezone.now().date():
            raise ValidationError("La fecha de uso debe ser hoy o en el futuro.")

        # 2) solapamiento de franjas horarias
        qs = Reserva.objects.filter(
            espacio=self.espacio,
            fecha_uso=self.fecha_uso
        ).exclude(pk=self.pk).filter(
            Q(hora_inicio__lt=self.hora_fin) &
            Q(hora_fin__gt=self.hora_inicio)
        )
        if qs.exists():
            raise ValidationError("Ya existe otra reserva solapada para este espacio.")


        # 3) si alguien aprueba o rechaza, debe ser administrador o moderador de ese mismo piso y ubicación
        if self.estado in [self.Estado.APROBADA, self.Estado.RECHAZADA] and self.aprobado_por:

            if self.aprobado_por.is_admin:
                return

            if not self.aprobado_por.is_moderador:
                raise ValidationError("Solo un administrador o moderador puede aprobar o rechazar reservas.")
            
            if (self.aprobado_por.ubicacion_id != self.espacio.ubicacion_id or
                self.aprobado_por.piso        != self.espacio.piso):
                raise ValidationError(
                    "El moderador solo puede aprobar o rechazar reservas de su misma ubicación y piso."
                )
