from apps.reservas.models import Reserva
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from django.db import transaction, IntegrityError

class Command(BaseCommand):
    help = "comando de testeo para resetear todas las reservas, ponerlas en estado pendiente."
    def handle(self, *args, **options):


        if settings.DEBUG:
            print("DEBUG is True - Reseteando todas las reservas a estado PENDIENTE")
            Reserva.objects.all().update(
                estado=Reserva.Estado.PENDIENTE, mensaje_aprobar_rechazar="", aprobado_por=None
            )

        else:
            print("No estas en modo desarrollo - No se realizaron cambios a las reservas")