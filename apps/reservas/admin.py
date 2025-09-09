from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

from apps.reservas.models import TipoActividad, Reserva, ReservaEspacio, DetalleReservaFisico, DetalleReservaDigital

# Inlines para mostrar los detalles asociados a una ReservaEspacio
class DetalleReservaFisicoInline(admin.StackedInline):
    model = DetalleReservaFisico
    extra = 0
    can_delete = False
    
class DetalleReservaDigitalInline(admin.StackedInline):
    model = DetalleReservaDigital
    extra = 0
    can_delete = False

# Inline para mostrar espacios asociados a una reserva
class ReservaEspacioInline(admin.TabularInline):
    model = ReservaEspacio
    extra = 0
    fields = ('espacio', 'numero_participantes', 'ver_detalles')
    readonly_fields = ('ver_detalles',)
    
    def ver_detalles(self, obj):
        if obj.pk:
            url = reverse('admin:reservas_reservaespacio_change', args=[obj.pk])
            return format_html('<a href="{}">Ver detalles</a>', url)
        return "-"
    ver_detalles.short_description = "Detalles"

# Admin para ReservaEspacio con sus detalles asociados
class ReservaEspacioAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'espacio', 'numero_participantes', 'tipo_espacio', 'tiene_detalle')
    list_filter = ('espacio__tipo', 'espacio__disponible')
    search_fields = ('reserva__p00_solicitante', 'reserva__nombre_solicitante', 'espacio__nombre')
    raw_id_fields = ('reserva', 'espacio')
    
    def tipo_espacio(self, obj):
        return obj.espacio.get_tipo_display() if obj.espacio else "-"
    tipo_espacio.short_description = "Tipo de Espacio"
    
    def tiene_detalle(self, obj):
        try:
            if hasattr(obj, 'detalle_digital') and obj.detalle_digital:
                return "Digital"
            elif hasattr(obj, 'detalle_fisico') and obj.detalle_fisico:
                return "Físico"
            return "No"
        except:
            return "Error"
    tiene_detalle.short_description = "Tiene Detalle"
    
    def get_inlines(self, request, obj):
        if obj and hasattr(obj, 'espacio') and obj.espacio:
            if obj.espacio.tipo == 'digital':
                return [DetalleReservaDigitalInline]
            elif obj.espacio.tipo == 'fisico':
                return [DetalleReservaFisicoInline]
        return []

# Admin para Reservas
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'p00_solicitante', 'nombre_solicitante', 'fecha_uso', 
                    'hora_inicio', 'hora_fin', 'estado', 'modalidad', 'cantidad_espacios')
    list_filter = ('estado', 'modalidad', 'fecha_uso', 'tipo_solicitud')
    search_fields = ('p00_solicitante', 'nombre_solicitante', 'email_solicitante')
    date_hierarchy = 'fecha_uso'
    readonly_fields = ('fecha_creacion',)
    inlines = [ReservaEspacioInline]
    fieldsets = (
        ('Información del Solicitante', {
            'fields': ('p00_solicitante', 'nombre_solicitante', 'email_solicitante', 
                      'telefono_solicitante', 'vicepresidencia_solicitante', 'gerencia_solicitante')
        }),
        ('Información de la Reserva', {
            'fields': ('modalidad', 'tipo_solicitud', 'tipo_actividad', 'fecha_uso', 
                      'hora_inicio', 'hora_fin', 'motivo', 'estado')
        }),
        ('Requerimientos y Observaciones', {
            'fields': ('requerimientos', 'observacion')
        }),
        ('Aprobación', {
            'fields': ('aprobado_por', 'mensaje_aprobar_rechazar', 'fecha_cambio_estado', 'fecha_creacion')
        }),
    )
    
    def cantidad_espacios(self, obj):
        return obj.espacios.count()
    cantidad_espacios.short_description = "Espacios"
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            espacios_count=Count('reserva_espacios')
        )
        return queryset

# Tipo de Actividad
class TipoActividadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'reservas_count')
    search_fields = ('nombre',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            reservas_count=Count('reservas')
        )
        return queryset
        
    def reservas_count(self, obj):
        return obj.reservas_count
    reservas_count.short_description = "Cantidad de Reservas"

# Registramos los modelos con sus clases Admin
admin.site.register(TipoActividad, TipoActividadAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(ReservaEspacio, ReservaEspacioAdmin)

