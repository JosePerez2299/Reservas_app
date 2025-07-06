import random
from datetime import timedelta, date, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from reservas.models import Reserva, Usuario, Espacio

class Command(BaseCommand):
    help = 'Crea un número especificado de reservas PENDIENTES por cada ubicación con espacios disponibles.'

    def add_arguments(self, parser):
        parser.add_argument(
            'total',
            type=int,
            help='Número de reservas PENDIENTES a crear en cada ubicación.',
            nargs='?',
            default=10
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada sobre errores y creación de reservas.'
        )

    def handle(self, *args, **kwargs):
        reservas_por_ubicacion = kwargs['total']
        verbose = kwargs.get('verbose', False)
        
        usuarios = list(Usuario.objects.filter(is_superuser=False))
        
        # Obtener ubicaciones únicas de espacios disponibles
        ubicaciones = Espacio.objects.filter(disponible=True).values_list('ubicacion', flat=True).distinct()
        
        if not usuarios:
            self.stdout.write(self.style.ERROR('No hay usuarios en la base de datos. Crea usuarios primero (ej. con crear_usuarios_demo).'))
            return

        if not ubicaciones:
            self.stdout.write(self.style.ERROR('No hay ubicaciones con espacios disponibles en la base de datos.'))
            return

        total_reservas_objetivo = reservas_por_ubicacion * len(ubicaciones)
        reservas_creadas = 0
        intentos = 0
        errores_contados = {
            'solapamiento': 0,
            'constraint_usuario': 0,
            'validacion': 0,
            'otros': 0
        }

        self.stdout.write(f'Intentando crear {reservas_por_ubicacion} reservas pendientes en cada una de las {len(ubicaciones)} ubicaciones...')
        self.stdout.write(f'Total objetivo: {total_reservas_objetivo} reservas')

        # Iterar por cada ubicación
        for ubicacion in ubicaciones:
            espacios_ubicacion = list(Espacio.objects.filter(disponible=True, ubicacion=ubicacion))
            reservas_ubicacion = 0
            
            if verbose:
                self.stdout.write(f'\n--- Procesando ubicación: {ubicacion} ---')
                self.stdout.write(f'Espacios disponibles: {len(espacios_ubicacion)}')
            
            # Crear reservas_por_ubicacion reservas en esta ubicación
            intentos_ubicacion = 0
            while reservas_ubicacion < reservas_por_ubicacion and intentos_ubicacion < reservas_por_ubicacion * 10:
                usuario = random.choice(usuarios)
                espacio = random.choice(espacios_ubicacion)
                
                # Fechas aleatorias en el próximo mes
                dias_futuro = random.randint(1, 30)
                fecha_uso = timezone.now().date() + timedelta(days=dias_futuro)

                # Horas aleatorias entre las 8am y 8pm, con más variación
                start_hour = random.randint(8, 19)
                duration_hours = random.randint(1, 4)
                hora_inicio = time(start_hour, random.choice([0, 30]))  # Permitir medias horas
                
                # Calcular hora_fin asegurando que no pase de las 22:00
                end_hour = min(22, start_hour + duration_hours)
                hora_fin = time(end_hour, random.choice([0, 30]))
                
                # Asegurar que hora_inicio < hora_fin
                if hora_inicio >= hora_fin:
                    continue

                # Motivo variado
                motivos = [
                    f"Reunión de trabajo en {espacio.nombre}",
                    f"Sesión de estudio grupal",
                    f"Presentación de proyecto",
                    f"Taller de capacitación",
                    f"Reunión de equipo",
                    f"Conferencia virtual",
                    f"Brainstorming creativo"
                ]
                motivo = random.choice(motivos)

                try:
                    # Crear instancia sin guardar para validar - SOLO PENDIENTES
                    reserva = Reserva(
                        usuario=usuario,
                        espacio=espacio,
                        fecha_uso=fecha_uso,
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        estado=Reserva.Estado.PENDIENTE,  # Solo pendientes
                        motivo=motivo,
                        aprobado_por=None,  # Sin aprobar
                        motivo_admin=""     # Sin motivo admin
                    )
                    
                    # Ejecutar validaciones del modelo
                    reserva.full_clean()
                    
                    # Si pasa las validaciones, guardar
                    reserva.save()
                    reservas_creadas += 1
                    reservas_ubicacion += 1
                    
                    if verbose:
                        self.stdout.write(
                            f'✓ Reserva creada: {usuario.username} - {espacio.nombre} - '
                            f'{fecha_uso} {hora_inicio}-{hora_fin} (PENDIENTE)'
                        )
                        
                except ValidationError as e:
                    if verbose:
                        self.stdout.write(f'✗ Error de validación: {e}')
                    
                    # Categorizar errores para estadísticas
                    error_msg = str(e)
                    if 'solapada' in error_msg.lower():
                        errores_contados['solapamiento'] += 1
                    else:
                        errores_contados['validacion'] += 1
                        
                except IntegrityError as e:
                    if verbose:
                        self.stdout.write(f'✗ Error de integridad: {e}')
                    
                    error_msg = str(e)
                    if 'uniq_usuario_espacio_fecha' in error_msg:
                        errores_contados['constraint_usuario'] += 1
                    else:
                        errores_contados['otros'] += 1
                        
                except Exception as e:
                    if verbose:
                        self.stdout.write(f'✗ Error inesperado: {e}')
                    errores_contados['otros'] += 1
                
                intentos += 1
                intentos_ubicacion += 1
            
            if verbose:
                self.stdout.write(f'Reservas creadas en {ubicacion}: {reservas_ubicacion}/{reservas_por_ubicacion}')

        # Mostrar resultados
        if reservas_creadas > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'¡Éxito! Se crearon {reservas_creadas} reservas PENDIENTES en {len(ubicaciones)} ubicaciones ({reservas_creadas}/{total_reservas_objetivo} objetivo).'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'No se pudo crear ninguna reserva pendiente en {intentos} intentos.'
                )
            )

        # Mostrar estadísticas de errores si hay verbose o si no se crearon todas las reservas
        if verbose or reservas_creadas < total_reservas_objetivo:
            self.stdout.write('\n--- Estadísticas de errores ---')
            total_errores = sum(errores_contados.values())
            if total_errores > 0:
                for tipo, cantidad in errores_contados.items():
                    if cantidad > 0:
                        porcentaje = (cantidad / total_errores) * 100
                        self.stdout.write(f'{tipo.capitalize()}: {cantidad} ({porcentaje:.1f}%)')
            else:
                self.stdout.write('No se registraron errores específicos.')

        # Sugerencias si hay muchos errores
        if reservas_creadas < total_reservas_objetivo * 0.5:  # Si se crearon menos del 50% esperado
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 Sugerencias para mejorar la tasa de éxito:'
                )
            )
            if errores_contados['solapamiento'] > 0:
                self.stdout.write('  - Considera limpiar reservas existentes o usar fechas más lejanas')
            if errores_contados['constraint_usuario'] > 0:
                self.stdout.write('  - Hay muchos usuarios con reservas del mismo día, considera más variación')
            if errores_contados['otros'] > 0:
                self.stdout.write('  - Revisa la configuración de espacios y usuarios')