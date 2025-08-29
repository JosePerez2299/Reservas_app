from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, F
from apps.espacios.models import Espacio
from apps.usuarios.models import Usuario
from apps.core.models import Ubicacion


# ——— 4. Reserva ————————————————————————————————————————————————
class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada',  'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='reservas'
    )
    espacio = models.ForeignKey(
        Espacio, on_delete=models.CASCADE, related_name='reservas'
    )
    fecha_uso = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()   
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.PENDIENTE
    )
    motivo = models.TextField(
        "Motivo de reserva", null=False, blank=False
    )
    motivo_admin = models.TextField(
        "Mensaje de aprobación/rechazo", null=True, blank=True, default=""
    )
    aprobado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reservas_aprobadas'
    )

    numero_participantes = models.IntegerField(
        "Número de participantes", null=False, blank=False, default=1
    )

    fecha_creacion = models.DateTimeField(
        "Fecha de creación", auto_now_add=True
    )
    fecha_cambio_estado = models.DateTimeField(
        "Fecha de cambio de estado", null=True, blank=True
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_uso', 'hora_inicio']
        indexes = [
            models.Index(fields=['espacio', 'fecha_uso']),
            models.Index(fields=['fecha_uso']),
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
        return f"US:{self.usuario.username} | ESP:{self.espacio.nombre}"


    def tipo_reserva(self):
        return self.espacio.tipo

    def clean(self):
        super().clean()

        # 0) Espacio disponible (solo si espacio ya ha sido asignado)
        if self.espacio_id is not None and not self.espacio.disponible:
            raise ValidationError("El espacio no está disponible.")

        # 1) fecha en el futuro o hoy
        if self.fecha_uso < timezone.now().date():
            raise ValidationError(
                "La fecha de uso debe ser hoy o en el futuro.")

        # 2) solapamiento de franjas horarias
        qs = Reserva.objects.filter(
            espacio_id=self.espacio_id,
            fecha_uso=self.fecha_uso,
            estado=self.Estado.APROBADA
        ).exclude(pk=self.pk).filter(
            Q(hora_inicio__lt=self.hora_fin) &
            Q(hora_fin__gt=self.hora_inicio)
        )
        if qs.exists():
            raise ValidationError(
                "Ya existe otra reserva solapada para este espacio.")

        # 3) si alguien aprueba o rechaza, debe ser administrador o moderador de ese mismo piso y ubicación
        if self.estado in [self.Estado.APROBADA, self.Estado.RECHAZADA]:
            if not self.aprobado_por:
                raise ValidationError(
                    "Debe haber un moderador o administrador que apruebe o rechace la reserva.")

            if self.aprobado_por.is_admin:
                return

            if not self.aprobado_por.is_moderador:
                raise ValidationError(
                    "Solo un administrador o moderador puede aprobar o rechazar reservas.")

            if (self.aprobado_por.ubicacion_id != self.espacio.ubicacion_id or
                    self.aprobado_por.piso != self.espacio.piso):
                raise ValidationError(
                    "El moderador solo puede aprobar o rechazar reservas de su misma ubicación y piso."
                )


class DetalleReservaDigital(models.Model):
    # To do: Validar que reserva.espacio.tipo == 'digital'
    # To do: Reserva unique constraint
    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name='detalles'
    )

    anfitrion_usuario = models.CharField(max_length=100, null=True, blank=True)

    ubicacion_transmision = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE, related_name='reservas_digitales', null=True, blank=True
    )

    # Espacio donde se realizara la transmisión
    espacio_transmision = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Detalle Reserva Digital"
        verbose_name_plural = "Detalles de Reservas Digitales"
        ordering = ['-reserva__fecha_uso', 'reserva__hora_inicio']
        indexes = [
            models.Index(fields=['reserva']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['reserva'],
                name='uniq_reserva_digital',
                violation_error_message="Ya existe un detalle de reserva digital para esta reserva."
            ),
        ]

    def __str__(self):
        return f"Reserva: {self.reserva.id} | Anfitrion: {self.anfitrion_usuario}"



class RequerimientoReserva(models.Model):

    class Tipo(models.TextChoices):
        PRODUCCION = 'produccion', 'Producción'
        COMUNICACIONAL = 'comunicacional', 'Comunicacional'
        OTRO = 'otro', 'Otro'

    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name='requerimientos'
    )

    nombre = models.CharField(max_length=100)
    observacion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=100, choices=Tipo.choices)

    class Meta:
        verbose_name = "Requerimiento de Reserva"
        verbose_name_plural = "Requerimientos de Reservas"
        ordering = ['-reserva__fecha_uso', 'reserva__hora_inicio']
