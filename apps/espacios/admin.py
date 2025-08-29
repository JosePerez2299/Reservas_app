# admin.py
from django.contrib import admin
from .models import Espacio, DetalleEspacioDigital, DetalleEspacioFisico


class DetalleDigitalInline(admin.StackedInline):
    model = DetalleEspacioDigital
    can_delete = False
    max_num = 1
    extra = 0
    verbose_name = "Detalle digital"
    verbose_name_plural = "Detalle digital"

class DetalleFisicoInline(admin.StackedInline):
    model = DetalleEspacioFisico
    can_delete = False
    max_num = 1
    extra = 0
    verbose_name = "Detalle físico"
    verbose_name_plural = "Detalle físico"

@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "capacidad_maxima", "get_plataforma", "get_piso")
    inlines = [DetalleDigitalInline, DetalleFisicoInline]
    readonly_fields = ()  # añadir si quieres campos sólo lectura

    def get_inline_instances(self, request, obj=None):
        """
        Mostrar solo el inline que corresponde al tipo del objeto ya creado.
        No mostrar inlines al crear (obj is None) para evitar crear detalles huérfanos.
        """
        inline_instances = []
        if not obj:
            return inline_instances

        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            if inline.model is DetalleEspacioDigital and obj.tipo == Espacio.Tipo.DIGITAL:
                inline_instances.append(inline)
            if inline.model is DetalleEspacioFisico and obj.tipo == Espacio.Tipo.FISICO:
                inline_instances.append(inline)
        return inline_instances

    # Métodos para mostrar campos del detalle de forma segura
    def get_plataforma(self, obj):
        return getattr(getattr(obj, 'detalle_digital', None), 'plataforma', None)
    get_plataforma.short_description = "Plataforma"

    def get_piso(self, obj):
        return getattr(getattr(obj, 'detalle_fisico', None), 'piso', None)
    get_piso.short_description = "Piso"
