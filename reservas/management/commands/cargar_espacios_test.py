import random
from django.core.management.base import BaseCommand
from reservas.models import Espacio  # Cambia 'espacios' si tu app tiene otro nombre

class Command(BaseCommand):
    help = 'Crea 1000 espacios de prueba para poblar la base de datos.'

    def handle(self, *args, **kwargs):
        tipos = [choice[0] for choice in Espacio.TIPO_CHOICES]
        ubicaciones = [
            "Edificio A", "Edificio B", "Edificio C",
            "Laboratorio Norte", "Laboratorio Sur",
            "Piso 1", "Piso 2", "Piso 3", "Aula Magna", "Anexo"
        ]

        espacios = []
        for i in range(1000):
            espacio = Espacio(
                nombre=f"Espacio {i+1}",
                ubicacion=random.choice(ubicaciones),
                capacidad=random.randint(10, 200),
                tipo=random.choice(tipos),
                disponible=random.choice([True, False])
            )
            espacios.append(espacio)

        Espacio.objects.bulk_create(espacios)
        self.stdout.write(self.style.SUCCESS('Se crearon 1000 espacios correctamente.'))
