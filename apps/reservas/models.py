from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, F, OneToOneField
from apps.espacios.models import Espacio
from apps.usuarios.models import Usuario
from apps.core.models import Ubicacion

class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada',  'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'
        CANCELADA = 'cancelada', 'Cancelada'

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'presencial', 'Presencial'
        VIRTUAL = 'virtual', 'Virtual'
        MIXTA = 'mixta', 'Mixta'


    class TipoSolicitud(models.TextChoices):
        INTERNA = 'interna', 'Interna'
        EXTERNA = 'externa', 'Externa'


    p00_solicitante = models.CharField(max_length=100)
    
    nombre_solicitante = models.CharField(max_length=100)
    
    email_solicitante = models.EmailField()

    telefono_solicitante = models.CharField(max_length=100)

    vicepresidencia_solicitante = models.CharField(max_length=100)

    gerencia_solicitante = models.CharField(max_length=100)


    # Datos de la reserva
    modalidad = models.CharField(
        max_length=10, choices=Modalidad.choices, default=Modalidad.PRESENCIAL
    )
    tipo_solicitud = models.CharField(
        max_length=10, choices=TipoSolicitud.choices, default=TipoSolicitud.INTERNA
    )

    tipo_actividad = models.ForeignKey(
        "TipoActividad", on_delete=models.CASCADE, related_name='reservas', null=True, blank=True
    )

    fecha_uso = models.DateField(null=False, blank=False)

    hora_inicio = models.TimeField(null=False, blank=False)
    
    hora_fin = models.TimeField(null=False, blank=False)   
    
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.PENDIENTE
    )

    espacios = models.ManyToManyField(
        Espacio,
        through="ReservaEspacio",
        related_name="reservas"
    )

    motivo = models.TextField(
        "Motivo de reserva", null=False, blank=False
    )

    observacion = models.TextField(
        "Observación", null=True, blank=True
    )

    mensaje_aprobar_rechazar = models.TextField(
        "Mensaje de aprobación/rechazo/cancelación", null=True, blank=True, default=""
    )

    aprobado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reservas_aprobadas'
    )

    fecha_creacion = models.DateTimeField(
        "Fecha de creación", auto_now_add=True
    )
    fecha_cambio_estado = models.DateTimeField(
        "Fecha de cambio de estado", null=True, blank=True
    )

    requerimientos = models.JSONField(
        "Requerimientos", null=True, blank=True, default=list
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_uso', 'hora_inicio']
        indexes = [
            models.Index(fields=['fecha_uso']),
        ]
        constraints = [
            # Evita que un mismo usuario haga dos reservas el mismo día en el mismo espacio

            # Asegura hora_inicio < hora_fin
            models.CheckConstraint(
                check=Q(hora_inicio__lt=F('hora_fin')),
                name='check_hora_inicio_menor_fin',
                violation_error_message="La hora de inicio debe ser menor a la hora de fin."
            ),
        ]

    def __str__(self):
        return f"RES:{self.id} | US:{self.p00_solicitante} | FE:{self.fecha_uso} | HI:{self.hora_inicio} | HF:{self.hora_fin}"


    # def clean(self):
    #     super().clean()

    #     # 0) Espacio disponible (solo si espacio ya ha sido asignado)
    #     if self.espacio_id is not None and not self.espacio.disponible:
    #         raise ValidationError("El espacio no está disponible.")

    #     # 1) fecha en el futuro o hoy
    #     if self.fecha_uso < timezone.now().date():
    #         raise ValidationError(
    #             "La fecha de uso debe ser hoy o en el futuro.")

    #     # 2) solapamiento de franjas horarias
    #     qs = Reserva.objects.filter(
    #         espacio_id=self.espacio_id,
    #         fecha_uso=self.fecha_uso,
    #         estado=self.Estado.APROBADA
    #     ).exclude(pk=self.pk).filter(
    #         Q(hora_inicio__lt=self.hora_fin) &
    #         Q(hora_fin__gt=self.hora_inicio)
    #     )
    #     if qs.exists():
    #         raise ValidationError(
    #             "Ya existe otra reserva solapada para este espacio.")

    #     # 3) si alguien aprueba o rechaza, debe ser administrador o moderador de ese mismo piso y ubicación
    #     if self.estado in [self.Estado.APROBADA, self.Estado.RECHAZADA]:
    #         if not self.aprobado_por:
    #             raise ValidationError(
    #                 "Debe haber un moderador o administrador que apruebe o rechace la reserva.")

    #         if self.aprobado_por.is_admin:
    #             return

    #         if not self.aprobado_por.is_moderador:
    #             raise ValidationError(
    #                 "Solo un administrador o moderador puede aprobar o rechazar reservas.")

    #         if (self.aprobado_por.ubicacion_id != self.espacio.ubicacion_id or
    #                 self.aprobado_por.piso != self.espacio.piso):
    #             raise ValidationError(
    #                 "El moderador solo puede aprobar o rechazar reservas de su misma ubicación y piso."
    #             )

class ReservaEspacio(models.Model):
    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name='reserva_espacios'
    )

    espacio = models.ForeignKey(
        Espacio, on_delete=models.CASCADE, related_name='reserva_espacios'
    )

    numero_participantes = models.PositiveIntegerField(
        "Número de participantes", null=False, blank=False, default=1, validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Reserva Espacio"
        verbose_name_plural = "Reservas Espacios"
        constraints = [
            # Evita que se reserve el mismo espacio dos o más veces en la misma reserva
            models.UniqueConstraint(
                fields=['reserva', 'espacio'],
                name='uniq_reserva_espacio',
                violation_error_message="Ya existe una reserva para este espacio."
            ),
        ]

    def clean(self):
        super().clean()

        # 1) determinar tipo de espacio de forma segura y eficiente
        tipo = None
        if getattr(self, "espacio_id", None):
            # solo recuperamos el campo tipo (no toda la instancia)
            tipo = Espacio.objects.filter(pk=self.espacio_id).values_list("tipo", flat=True).first()
        else:
            # si espacio ya está asignado como instancia en memoria (p. ej. form.save(commit=False))
            espacio_obj = getattr(self, "espacio", None)
            if espacio_obj is not None:
                tipo = getattr(espacio_obj, "tipo", None)
        
        # En el proceso de creación mediante FormWizard, no podemos verificar detalle_digital/fisico
        # ya que estas relaciones aún no existen cuando se valida inicialmente el modelo
        try:
            has_detalle_digital = bool(self.detalle_digital)
        except ReservaEspacio.detalle_digital.RelatedObjectDoesNotExist:
            has_detalle_digital = False
            
        try:
            has_detalle_fisico = bool(self.detalle_fisico)
        except ReservaEspacio.detalle_fisico.RelatedObjectDoesNotExist:
            has_detalle_fisico = False
        
        # Solo validamos si ya existen los detalles (en edición o después de creación)
        if self.pk and has_detalle_digital == has_detalle_fisico:
            raise ValidationError("Debe rellenar exactamente uno de 'detalle_digital' o 'detalle_fisico'.")

        # 3) validaciones según tipo - solo aplicamos si tenemos un tipo definido
        if tipo == "fisico":
            if self.pk and not has_detalle_fisico and has_detalle_digital:
                raise ValidationError("Para un espacio físico debe asignar 'detalle_fisico'.")
        elif tipo == "digital":
            if self.pk and not has_detalle_digital and has_detalle_fisico:
                raise ValidationError("Para un espacio digital debe asignar 'detalle_digital'.")


        # 4) Validar que no exista una reserva aprobada para el espacio seleccionado en ese horario
        if hasattr(self, 'espacio') and hasattr(self, 'reserva'):
            # Buscar reservas aprobadas del mismo espacio en la misma fecha que se solapan con el horario
            reservas_solapadas = ReservaEspacio.objects.filter(
                espacio=self.espacio,
                reserva__fecha_uso=self.reserva.fecha_uso,
                reserva__estado=Reserva.Estado.APROBADA
            ).exclude(
                reserva=self.reserva  # Excluir la reserva actual si estamos editando
            ).filter(
                # Condición para detectar solapamiento de horarios:
                # (hora_inicio < hora_fin_nueva) AND (hora_fin > hora_inicio_nueva)
                Q(reserva__hora_inicio__lt=self.reserva.hora_fin) &
                Q(reserva__hora_fin__gt=self.reserva.hora_inicio)
            )
            
            if reservas_solapadas.exists():
                raise ValidationError(
                    "Ya existe una reserva aprobada para este espacio en la fecha y horario seleccionados."
                )
        
        

    def __str__(self):
        return f"Reserva: {self.reserva.id} | Espacio: {self.espacio.nombre}"


class DetalleReservaDigital(models.Model):
    # To do: Validar que reserva.espacio.tipo == 'digital'
    # To do: Reserva unique constraint
    reserva_espacio = OneToOneField(
        ReservaEspacio, on_delete=models.CASCADE, related_name='detalle_digital'
    )

    anfitrion_usuario = models.CharField(max_length=100, null=True, blank=True)
    
    # Ubicacion donde se realizara la transmision
    ubicacion_transmision = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE, related_name='reservas_digitales', null=True, blank=True
    )

    #  Nombre del espacio donde se realizara la transmisión
    espacio_transmision = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Detalle Reserva Digital"
        verbose_name_plural = "Detalles de Reservas Digitales"
        ordering = ['-reserva_espacio__reserva__fecha_uso', 'reserva_espacio__reserva__hora_inicio']
        indexes = [
            models.Index(fields=['reserva_espacio']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['reserva_espacio'],
                name='uniq_reserva_digital',
                violation_error_message="Ya existe un detalle de reserva digital para esta reserva."
            ),
        ]

    def __str__(self):
        return f"Reserva: {self.reserva_espacio}"


class DetalleReservaFisico(models.Model):
    reserva_espacio = OneToOneField(
        ReservaEspacio, on_delete=models.CASCADE, related_name='detalle_fisico'
    )
    
    # Campos específicos para reservas de espacios físicos
    numero_participantes_confirmados = models.IntegerField(
        "Número de participantes confirmados", null=True, blank=True, default=0
    )
    
    class Meta:
        verbose_name = "Detalle Reserva Físico"
        verbose_name_plural = "Detalles de Reservas Físicas"
        indexes = [
            models.Index(fields=['reserva_espacio']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['reserva_espacio'],
                name='uniq_reserva_fisico',
                violation_error_message="Ya existe un detalle de reserva físico para esta reserva."
            ),
        ]

    def __str__(self):
        return f"Reserva: {self.reserva_espacio}"


class TipoActividad(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tipo de Actividad"
        verbose_name_plural = "Tipos de Actividades"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre