# usuarios/management/commands/create_sample_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from django.db import transaction, IntegrityError

class Command(BaseCommand):
    help = "Crea 4 usuarios de ejemplo: 2 usuarios en el grupo 'usuario' y 2 en 'administrador'."

    def handle(self, *args, **options):
        User = get_user_model()

        # Nombres de grupos (toma settings.GRUPOS si está definido)
        GR = getattr(settings, 'GRUPOS', None)
        if GR:
            ADMIN_NAME = GR.ADMINISTRADOR
            USER_NAME = GR.USUARIO
        else:
            ADMIN_NAME = 'administrador'
            USER_NAME = 'usuario'

        # Asegurar existencia de grupos
        admin_group, _ = Group.objects.get_or_create(name=ADMIN_NAME)
        user_group, _ = Group.objects.get_or_create(name=USER_NAME)

        # Usuarios a crear (modifica emails/passwords según prefieras)
        sample_users = [
            {
                'username': 'usuario1',
                'email': '16-10882+usuario1@usb.ve',
                'p00': '150000',
                'first_name': 'Juan',
                'last_name': 'Perez',
                'telefono': '1234567890',
                'password': 'usuario123',
                'vicepresidencia': 'Vicepresidencia 1',
                'gerencia': 'Gerencia 1',
                'group': user_group
            },
            {
                'username': 'usuario2',
                'email': '16-10882+usuario2@usb.ve',
                'p00': '150001',
                'first_name': 'Maria',
                'last_name': 'Gonzalez',
                'telefono': '1234567890',
                'password': 'usuario123',
                'vicepresidencia': 'Vicepresidencia 2',
                'gerencia': 'Gerencia 2',
                'group': user_group
            },
            {
                'username': 'admin1',
                'email': '16-10882+admin1@usb.ve',
                'p00': '150002',
                'first_name': 'Juan',
                'last_name': 'Perez',
                'telefono': '1234567890',
                'password': 'admin123',
                'vicepresidencia': 'Vicepresidencia 3',
                'gerencia': 'Gerencia 3',
                'group': admin_group
            },
            {
                'username': 'admin2',
                'email': '16-10882+admin2@usb.ve',
                'p00': '150003',
                'first_name': 'Luis',
                'last_name': 'Fernandez',
                'telefono': '1234567890',
                'password': 'admin123',
                'vicepresidencia': 'Vicepresidencia 4',
                'gerencia': 'Gerencia 4',
                'group': admin_group
            },
        ]

        for u in sample_users:
            try:
                with transaction.atomic():
                    existing = User.objects.filter(username=u['username']).first()
                    if existing:
                        # usuario ya existe: asegurar que pertenezca al grupo
                        if not existing.groups.filter(id=u['group'].id).exists():
                            existing.groups.add(u['group'])
                            self.stdout.write(self.style.SUCCESS(
                                f"Usuario existente '{u['username']}' actualizado: agregado al grupo '{u['group'].name}'."
                            ))
                        else:
                            self.stdout.write(f"Usuario existente '{u['username']}' ya pertenece al grupo '{u['group'].name}'.")
                        # opcional: sincronizar correo/p00 si quieres:
                        # existing.email = u['email']; existing.p00 = u['p00']; existing.save()
                        continue

                    # Verificar p00 único
                    if User.objects.filter(p00=u['p00']).exists():
                        raise IntegrityError(f"p00 '{u['p00']}' ya existe en la base de datos. Ajusta sample_users.")

                    # Crear usuario
                    user = User.objects.create_user(
                        username=u['username'],
                        email=u['email'],
                        p00='P00'+u['p00'],
                        password=u['password'],
                        telefono=u['telefono'],
                        first_name=u['first_name'],
                        last_name=u['last_name'],
                        vicepresidencia=u['vicepresidencia'],
                        gerencia=u['gerencia'],
                    )
                    # Asignar campos adicionales y guardar
                    user.save()

                    # Añadir al grupo
                    user.groups.add(u['group'])

                    self.stdout.write(self.style.SUCCESS(
                        f"Usuario creado: {u['username']} (grupo: {u['group'].name})"
                    ))
            except IntegrityError as e:
                self.stderr.write(self.style.ERROR(f"Error creando '{u['username']}': {e}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error inesperado para '{u['username']}': {e}"))

        self.stdout.write(self.style.SUCCESS("Proceso terminado."))
