from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.usuarios.models import Ubicacion


class PlataformaDigital(models.Model):
    nombre = models.CharField(max_length=100)
    url = models.URLField(max_length=200)

    class Meta:
        verbose_name = "Plataforma Digital"
        verbose_name_plural = "Plataformas Digitales"

    def __str__(self):
        return f"{self.nombre}"




class Espacio(models.Model):

    class Tipo(models.TextChoices):
        FISICO = 'fisico', 'Físico'
        DIGITAL = 'digital', 'Digital'

    nombre = models.CharField(max_length=20, unique=True, blank=False,
                              validators=[
                                  RegexValidator(
                                      r"^[a-zA-Z][a-zA-Z0-9 ]*",
                                      message="El nombre del espacio debe comenzar con una letra, y solo puede contener letras, números y espacios."
                                  )
                              ])

    capacidad_maxima = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5000), MinValueValidator(1)],
        help_text="Capacidad máxima (≤ 5000)"
    )

    tipo = models.CharField(
        max_length=20, choices=Tipo.choices)
  
    disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    descripcion = models.TextField(
        "Descripción", null=True, blank=True
    )

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Espacio"
        verbose_name_plural = "Espacios"
        ordering = ['tipo',  'nombre']
        indexes = [
            models.Index(fields=['tipo'])
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(capacidad_maxima__lte=5000),
                name='check_capacidad_max_5000'
            ),
        ]

    def ubicacion(self):
        if self.tipo == 'fisico':
            return self.detalles_fisicos.first().ubicacion.nombre
        return self.detalles_digitales.first().plataforma.nombre

    def __str__(self):
        return f"{self.nombre}"


class DetalleEspacioDigital(models.Model):
    espacio = models.ForeignKey(
        Espacio, on_delete=models.CASCADE, related_name='detalles_digitales')

    plataforma = models.ForeignKey(
        PlataformaDigital, on_delete=models.CASCADE, related_name='detalles')

    class Meta:
        verbose_name = "Detalle Espacio Digital"
        verbose_name_plural = "Detalles de Espacios Digitales"
        constraints = [
            models.UniqueConstraint(
                fields=['espacio'],
                name='uniq_espacio_digital',
                violation_error_message="Ya existe un detalle de espacio digital para este espacio."
            )
        ]

    def clean(self):
        super().clean()
        
        # Validar que el espacio sea de tipo digital
        if self.espacio and self.espacio.tipo != 'digital':
            raise ValidationError({
                'espacio': f'El espacio "{self.espacio.nombre}" debe ser de tipo digital para tener detalles digitales.'
            })
        
        # Validar que no existan detalles físicos para el mismo espacio
        if self.espacio and hasattr(self.espacio, 'detalles_fisicos') and self.espacio.detalles_fisicos.exists():
            raise ValidationError({
                'espacio': f'El espacio "{self.espacio.nombre}" ya tiene detalles físicos. No puede tener ambos tipos de detalles.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Espacio: {self.espacio.nombre} | Capacidad Máxima: {self.espacio.capacidad_maxima}"


class DetalleEspacioFisico(models.Model):
    class Tipo(models.TextChoices):
        SALON = 'salon', 'Salón'
        LABORATORIO = 'laboratorio', 'Laboratorio'
        AUDITORIO = 'auditorio', 'Auditorio'

    espacio = models.ForeignKey(
        Espacio, on_delete=models.CASCADE, related_name='detalles_fisicos')
    piso = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="Piso en que se encuentra el espacio (≤ 40)"
    )
    tipo = models.CharField(
        max_length=20, choices=Tipo.choices)
    
    ubicacion = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE, related_name='espacios_fisicos')

    class Meta:
        verbose_name = "Detalle Espacio Físico"
        verbose_name_plural = "Detalles de Espacios Físicos"
        constraints = [
            models.UniqueConstraint(
                fields=['espacio'],
                name='uniq_espacio_fisico',
                violation_error_message="Ya existe un detalle de espacio físico para este espacio."
            )
        ]

    def clean(self):
        super().clean()
        
        # Validar que el espacio sea de tipo físico
        if self.espacio and self.espacio.tipo != 'fisico':
            raise ValidationError({
                'espacio': f'El espacio "{self.espacio.nombre}" debe ser de tipo físico para tener detalles físicos.'
            })
        
        # Validar que no existan detalles digitales para el mismo espacio
        if self.espacio and hasattr(self.espacio, 'detalles_digitales') and self.espacio.detalles_digitales.exists():
            raise ValidationError({
                'espacio': f'El espacio "{self.espacio.nombre}" ya tiene detalles digitales. No puede tener ambos tipos de detalles.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Espacio: {self.espacio.nombre} | Capacidad Máxima: {self.espacio.capacidad_maxima}"


