from django.db import models

# Create your models here.

# ——— 1. Ubicación —————————————————————————————————————————————
class Ubicacion(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Ubicaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PlataformaDigital(models.Model):
    nombre = models.CharField(max_length=100)
    url = models.URLField(max_length=200)

    class Meta:
        verbose_name = "Plataforma Digital"
        verbose_name_plural = "Plataformas Digitales"

    def __str__(self):
        return f"{self.nombre}"


