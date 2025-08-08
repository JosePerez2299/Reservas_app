from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from apps.usuarios.models import Ubicacion, Usuario

# Create your models here.


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
                    message="El nombre del espacio debe comenzar con una letra, y solo puede contener letras, números y espacios."
                )
        ]) 
    ubicacion   = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    piso        = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="Piso en que se encuentra el espacio (≤ 40)"
    )
    capacidad   = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(1000),MinValueValidator(1)],
        help_text="Capacidad máxima (≤ 1000)"
    )
    tipo        = models.CharField(max_length=20, choices=Tipo.choices)
    disponible  = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now=True)

    descripcion = models.TextField(
        "Descripción", null=True, blank=True
    )
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
