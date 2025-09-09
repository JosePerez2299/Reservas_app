from django.contrib import admin

from apps.reservas.models import TipoActividad, Reserva, ReservaEspacio, DetalleReservaFisico, DetalleReservaDigital

# Register your models here.
admin.site.register(TipoActividad)
admin.site.register(Reserva)
admin.site.register(ReservaEspacio)
admin.site.register(DetalleReservaFisico)
admin.site.register(DetalleReservaDigital)

