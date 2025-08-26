from django.contrib import admin

# Register your models here.
from .models import Espacio, PlataformaDigital, DetalleEspacioDigital, DetalleEspacioFisico

admin.site.register(Espacio)
admin.site.register(PlataformaDigital)
admin.site.register(DetalleEspacioDigital)
admin.site.register(DetalleEspacioFisico)

