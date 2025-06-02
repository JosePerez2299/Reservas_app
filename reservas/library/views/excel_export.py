from django.http import HttpResponse
from django.views import View
from .models import Reserva
from reservas.resources import UsuarioResource

class UsuarioExportExcel(View):
    def get(self, request, *args, **kwargs):
        # Filtra o adapta tu QuerySet según necesidad. Aquí obj obtendrá todas las usuarios.
        queryset =  Usuario.objects.all()

        # Instancia el Resource y conviértelo a formato Excel
        resource = UsuarioResource()
        dataset = resource.export(queryset)  # dataset es un tablib.Dataset

        # Construimos la respuesta HTTP con el contenido Excel
        response = HttpResponse(
            dataset.xlsx,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="usuarios.xlsx"'
        return response
