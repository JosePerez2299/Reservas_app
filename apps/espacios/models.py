from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
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

    class TipoUbicacion(models.TextChoices):
        FISICO = 'fisico', 'Físico'
        DIGITAL = 'digital', 'Digital'

    class Tipo(models.TextChoices):
        SALON = 'salon', 'Salón'
        LABORATORIO = 'laboratorio', 'Laboratorio'
        AUDITORIO = 'auditorio', 'Auditorio'

    nombre = models.CharField(max_length=20, unique=True, blank=False,
                              validators=[
                                  RegexValidator(
                                      r"^[a-zA-Z][a-zA-Z0-9 ]*",
                                      message="El nombre del espacio debe comenzar con una letra, y solo puede contener letras, números y espacios."
                                  )
                              ])


    capacidad_maxima = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(1)],
        help_text="Capacidad máxima (≤ 1000)"
    )

    tipo_ubicacion = models.CharField(
        max_length=20, choices=TipoUbicacion.choices)
  
    disponible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    descripcion = models.TextField(
        "Descripción", null=True, blank=True
    )

    class Meta:
        verbose_name = "Espacio"
        verbose_name_plural = "Espacios"
        ordering = ['tipo_ubicacion',  'nombre']
        indexes = [
            models.Index(fields=['tipo_ubicacion'])
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(capacidad_maxima__lte=1000),
                name='check_capacidad_max_1000'
            ),
            models.CheckConstraint(
                check=Q(tipo_ubicacion='digital') & Q(tipo__isnull=True),
                name='check_tipo_digital_no_nulo',
                violation_error_message="El tipo de espacio debe ser nulo si el espacio es digital."
            ),
            models.CheckConstraint(
                check=Q(tipo_ubicacion='fisico') & Q(tipo__isnull=False),
                name='check_tipo_fisico_no_nulo',
                violation_error_message="El tipo de espacio debe ser no nulo si el espacio es físico."
            ),
        ]

    def ubicacion(self):
        if self.tipo_ubicacion == 'fisico':
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

    def __str__(self):
        return f"Espacio: {self.espacio.nombre} | Capacidad Máxima: {self.capacidad_maxima}"


class DetalleEspacioFisico(models.Model):
    espacio = models.ForeignKey(
        Espacio, on_delete=models.CASCADE, related_name='detalles_fisicos')
    piso = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="Piso en que se encuentra el espacio (≤ 40)"
    )
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
            ),
        ]


    def __str__(self):
        return f"Espacio: {self.espacio.nombre} | Capacidad Máxima: {self.capacidad_maxima}"
