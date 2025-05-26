# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.db.models import Q, F
from django.core.validators import RegexValidator

# ——— 1. Ubicación —————————————————————————————————————————————
class Ubicacion(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Ubicaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ——— 2. Usuario personalizado ————————————————————————————————————
class Usuario(AbstractUser):
    email = models.EmailField('email address', unique=True)
    ubicacion = models.ForeignKey(
        Ubicacion, on_delete=models.SET_NULL, 
        null= True,
        help_text="La sede/edificio al que pertenece el usuario", 
    )
    piso = models.PositiveSmallIntegerField(
        null = True,
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
        return self.groups.filter(name='moderador').exists()


# ——— 3. Espacio ———————————————————————————————————————————————
class Espacio(models.Model):
    TIPO_CHOICES = [
        ('salon', 'Salón'),
        ('laboratorio', 'Laboratorio'),
        ('auditorio', 'Auditorio'),
    ]

    nombre      = models.CharField(max_length=20, unique=True, blank=False,
            validators=[
                RegexValidator(
                   r"^[a-zA-Z][a-zA-Z0-9_ ]*[a-zA-Z0-9]$",
                    message="El nombre del espacio debe comenzar y terminar con una letra o número, y solo puede contener letras, números, guiones bajos y espacios."
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
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES)
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
        return f"{self.nombre} ({self.get_tipo_display()}) — {self.ubicacion}/{self.piso}"


# ——— 4. Reserva ————————————————————————————————————————————————
class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada',   'Aprobada'),
        ('rechazada',  'Rechazada'),
    ]

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
        max_length=10, choices=ESTADO_CHOICES, default='pendiente'
    )
    motivo       = models.TextField(null=False, blank=False)
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
                name='uniq_usuario_espacio_fecha'
            ),
            # Asegura hora_inicio < hora_fin
            models.CheckConstraint(
                check=Q(hora_inicio__lt=F('hora_fin')),
                name='check_hora_inicio_menor_fin'
            ),
        ]

    def __str__(self):
        return f"{self.espacio} — {self.fecha_uso} {self.hora_inicio}-{self.hora_fin}"

    def clean(self):
        super().clean()

        # 1) fecha en el futuro o hoy
        if self.fecha_uso < timezone.now:
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

        # 3) si alguien aprueba, debe ser moderador de ese mismo piso y ubicación
        if self.estado == 'aprobada' and self.aprobado_por:
            if not self.aprobado_por.is_moderador:
                raise ValidationError("Solo un moderador puede aprobar reservas.")
            if (self.aprobado_por.ubicacion_id != self.espacio.ubicacion_id or
                self.aprobado_por.piso        != self.espacio.piso):
                raise ValidationError(
                    "El moderador solo puede aprobar reservas de su misma ubicación y piso."
                )
