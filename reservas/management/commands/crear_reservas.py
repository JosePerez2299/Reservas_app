import random
from datetime import timedelta, date, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from reservas.models import Reserva, Usuario, Espacio

class Command(BaseCommand):
    help = 'Crea un número especificado de reservas de prueba con datos aleatorios.'

    def add_arguments(self, parser):
        parser.add_argument(
            'total',
            type=int,
            help='Indica el número total de reservas a crear.',
            nargs='?',
            default=10
        )

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        
        usuarios = list(Usuario.objects.filter(is_superuser=False))
        espacios = list(Espacio.objects.all())

        if not usuarios:
            self.stdout.write(self.style.ERROR('No hay usuarios en la base de datos. Crea usuarios primero (ej. con crear_usuarios_demo).'))
            return

        if not espacios:
            self.stdout.write(self.style.ERROR('No hay espacios en la base de datos. Cárgalos primero (ej. con cargar_espacios).'))
            return

        reservas_creadas = 0
        intentos = 0

        self.stdout.write(f'Intentando crear {total} reservas...')

        while reservas_creadas < total and intentos < total * 5:
            usuario = random.choice(usuarios)
            espacio = random.choice(espacios)
            
            # Fechas aleatorias en el próximo mes
            dias_futuro = random.randint(1, 30)
            fecha_uso = timezone.now().date() + timedelta(days=dias_futuro)

            # Horas aleatorias entre las 8am y 8pm
            start_hour = random.randint(8, 19)
            duration_hours = random.randint(1, 3)
            hora_inicio = time(start_hour, 0)
            hora_fin = time(min(22, start_hour + duration_hours), 0)

            # Estado aleatorio
            estado = random.choice([Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA, Reserva.Estado.RECHAZADA])
            
            # Motivo simple
            motivo = f"Reserva de prueba para {espacio.nombre} por {usuario.username}"

            aprobado_por = None
            motivo_admin = ""
            if estado != Reserva.Estado.PENDIENTE:
                moderadores = list(Usuario.objects.filter(groups__name='Moderador'))
                if moderadores:
                    aprobado_por = random.choice(moderadores)
                    motivo_admin = f"Estado cambiado por moderador: {aprobado_por.username}"

            try:
                Reserva.objects.create(
                    usuario=usuario,
                    espacio=espacio,
                    fecha_uso=fecha_uso,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    estado=estado,
                    motivo=motivo,
                    aprobado_por=aprobado_por,
                    motivo_admin=motivo_admin
                )
                reservas_creadas += 1
            except Exception as e:
                # La reserva puede fallar por restricciones (ej. UniqueConstraint)
                # Simplemente lo ignoramos e intentamos con otros datos
                pass
            
            intentos += 1

        if reservas_creadas > 0:
            self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se crearon {reservas_creadas} nuevas reservas.'))
        else:
            self.stdout.write(self.style.WARNING(f'No se pudo crear ninguna reserva nueva. Posiblemente por conflictos con reservas existentes.')) 