import random
from django.core.management.base import BaseCommand
from reservas.models import Espacio, Ubicacion

class Command(BaseCommand):
    help = 'Crea 1000 espacios de prueba para poblar la base de datos.'

    def handle(self, *args, **kwargs):
        tipos = [choice[0] for choice in Espacio.TIPO_CHOICES]

        # Trae todas las ubicaciones ya creadas
        ubicaciones = list(Ubicacion.objects.all())
        if not ubicaciones:
            self.stderr.write(self.style.ERROR(
                'No hay ubicaciones en la base de datos. '
                'Crea al menos una Ubicacion antes de ejecutar este comando.'
            ))
            return

        espacios = []
        for ubic in ubicaciones:
            for i in range(10):
                nombre_random = f"Espacio en {ubic.nombre}-{i+1}"
                espacio = Espacio(
                    nombre     = nombre_random,
                    ubicacion  = ubic,
                    piso       = 1,
                    capacidad  = random.randint(10, 200),
                    tipo       = random.choice(tipos),
                    disponible = random.choice([True, False]),
                )
                espacios.append(espacio)

        Espacio.objects.bulk_create(espacios)
        self.stdout.write(self.style.SUCCESS(
            f'Se crearon {len(espacios)} espacios correctamente.'
        ))
