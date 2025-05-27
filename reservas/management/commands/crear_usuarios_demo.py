import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from reservas.models import Ubicacion  # Asegúrate de importar correctamente tu modelo

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea 2 usuarios de cada grupo para cada ubicación existente'

    def handle(self, *args, **kwargs):
        password = '1234jose'

        # Definir o crear ubicaciones
        nombres_ubicaciones = ['edf1', 'edf2', 'edf3', 'edf4']
        ubicaciones = []
        for nombre in nombres_ubicaciones:
            ubicacion, _ = Ubicacion.objects.get_or_create(nombre=nombre)
            ubicaciones.append(ubicacion)
        self.stdout.write(self.style.SUCCESS('Ubicaciones procesadas.'))

        # Obtener todos los grupos existentes
        grupos = Group.objects.all()
        if not grupos:
            self.stdout.write(self.style.WARNING('No hay grupos definidos.'))
            return
        self.stdout.write(self.style.SUCCESS(f'Grupos encontrados: {[g.name for g in grupos]}'))

        # Para cada ubicación, crear 2 usuarios por cada grupo
        for ubicacion in ubicaciones:
            for grupo in grupos:
                for i in range(1, 3):  # Crear dos usuarios
                    base_username = f"{grupo.name.lower()}_{ubicacion.nombre.lower()}_{i}"
                    username = base_username
                    suffix = 1

                    # Asegurar que el username sea único
                    while User.objects.filter(username=username).exists():
                        suffix += 1
                        username = f"{base_username}{suffix}"

                    email = f"{username}@example.com"

                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        ubicacion=ubicacion,
                        piso=1
                    )
                    user.groups.add(grupo)

                    # Si el grupo es 'admin', asignar permisos de superusuario
                    if grupo.name.lower() == 'admin':
                        user.is_staff = True
                        user.is_superuser = True
                        user.save()

                    self.stdout.write(self.style.SUCCESS(
                        f'Usuario {username} creado en grupo {grupo.name} con ubicación {ubicacion.nombre}'
                    ))
