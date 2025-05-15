import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from reservas.models import Ubicacion  # Asegúrate de importar correctamente tu modelo

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea 2 ubicaciones y 2 usuarios por cada grupo existente'

    def handle(self, *args, **kwargs):
        password = '1234jose'

        # Crear ubicaciones si no existen
        nombres_ubicaciones = ['NEA', 'EQUIPOS II', 'ESTACIONAMIENTO', 'MEZANINA']
        ubicaciones = []

        for nombre in nombres_ubicaciones:
            ubicacion, _ = Ubicacion.objects.get_or_create(nombre=nombre)
            ubicaciones.append(ubicacion)

        self.stdout.write(self.style.SUCCESS('Ubicaciones creadas o ya existentes.'))

        grupos = Group.objects.all()

        if not grupos.exists():
            self.stdout.write(self.style.WARNING('No hay grupos definidos.'))
            return
        

        self.stdout.write(self.style.SUCCESS('Grupos: ' + str(grupos)))

        for grupo in grupos:
            for i in range(1, 3):  # 2 usuarios por grupo
                username = f"{grupo.name.lower()}{i}"
                email = f"{username}@example.com"
                ubicacion = random.choice(ubicaciones)

                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        ubicacion=ubicacion,
                        piso=1
                    )
                    user.groups.add(grupo)

                    if grupo.name.lower() == 'admin':
                        user.is_staff = True
                        user.is_superuser = True
                        user.save()

                    self.stdout.write(self.style.SUCCESS(
                        f'Usuario {username} creado en grupo {grupo.name} con ubicación {ubicacion.nombre}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(f'Usuario {username} ya existe.'))
