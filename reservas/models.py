from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Espacio(models.Model):
    TIPO_CHOICES = [
        ('salon', 'Salón'),
        ('laboratorio', 'Laboratorio'),
        ('auditorio', 'Auditorio'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=255)
    capacidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    fecha_uso = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    motivo = models.TextField()

    def __str__(self):
        return f"{self.usuario.username} - {self.espacio.nombre} ({self.fecha_uso})"
