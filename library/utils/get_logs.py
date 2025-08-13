from auditlog.models import LogEntry

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario


def get_logs(user):
    qs = LogEntry.objects.all()
    ct_reserva = ContentType.objects.get_for_model(Reserva)

    # Todos los logs de usuarios y moderadores, incluyendo a sí mismo
    if user.is_admin:
        filtro_usuario = Q(actor__groups__name__in=[ user.GRUPOS.MODERADOR, user.GRUPOS.USUARIO]) | Q(actor=user)
        return qs.filter(filtro_usuario)
    
    # Todos los logs de reservas de mi ubicación y piso, o donde el actor es el usuario
    if user.is_moderador:
        filtro_usuario = Q(actor=user)

        mis_reservas = Reserva.objects.filter(
            Q(Q(espacio__ubicacion=user.ubicacion) & Q(espacio__piso=user.piso)) |
            Q(usuario=user) |
            Q(aprobado_por=user)
        ).values_list('pk', flat=True)

        filtro_reserva_mi_ubicacion = Q(
            Q(content_type=ct_reserva) &
            Q(object_id__in=mis_reservas)
        )
        # Retornar todos los log donde actor es moderador o usuario
        qs = qs.filter(filtro_usuario | filtro_reserva_mi_ubicacion)
        return qs
    
    # Todos los logs de reservas de mi ubicación y piso, o donde el actor es el usuario
    if user.is_usuario:
        filtro_usuario = Q(actor=user)
        mis_reservas = Reserva.objects.filter(
            Q(usuario=user)
        ).values_list('pk', flat=True)
        
        filtro_reserva_mi_ubicacion = Q(
            Q(content_type=ct_reserva) &
            Q(object_id__in=mis_reservas)
        )
        # Retornar todos los log donde actor es usuario
        qs = qs.filter(filtro_usuario | filtro_reserva_mi_ubicacion)
        return qs
        