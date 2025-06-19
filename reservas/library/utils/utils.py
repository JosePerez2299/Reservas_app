from reservas.models import *
from datetime import datetime
from math import floor
    
def get_user_groups(user):
    """
    Devuelve una lista de nombres de los grupos a los que pertenece un usuario.

    Argumentos:
        user (User): Una instancia de usuario de Django.

    Retorna:
        list: Una lista de cadenas que representan los nombres de los grupos del usuario.
    """
    return [group.name for group in user.groups.all()]


def get_all_cols(model):
    """
    Devuelve una lista de nombres de los campos de un modelo.

    Argumentos:
        model (Model): Un modelo de Django.

    Retorna:
        list: Una lista de cadenas que representan los nombres de los campos del modelo.
    """
    return [field.name for field in model._meta.get_fields()]


def get_stats(request):
    try:
        logs = request.user.get_logs()[:5]
    except:
        logs = []
    if request.user.is_admin:
        stats = get_stats_administrador(request)
        stats['logs'] = logs
        return stats
    elif request.user.is_usuario:
        stats = get_stats_usuario(request)
        stats['logs'] = logs
        return stats
    elif request.user.is_moderador:
        stats = get_stats_moderador(request)
        stats['logs'] = logs
        return stats
    return {'cards': [], 'month_summary': [], 'logs': []}

def get_stats_administrador(request):
    month = datetime.now().month
    year = datetime.now().year
    reservas_pendientes = Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE).count()
    reservas_aprobadas = Reserva.objects.filter(estado=Reserva.Estado.APROBADA).count()
    reservas_rechazadas = Reserva.objects.filter(estado=Reserva.Estado.RECHAZADA).count()
    espacios_disponibles = Espacio.objects.filter(disponible=True).count()
    espacios_no_disponibles = Espacio.objects.filter(disponible=False).count()

    reservas_mes = Reserva.objects.filter(fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_aprobadas_mes = Reserva.objects.filter(estado=Reserva.Estado.APROBADA, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_pendientes_mes = Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_rechazadas_mes = Reserva.objects.filter(estado=Reserva.Estado.RECHAZADA, fecha_uso__month=month, fecha_uso__year=year).count()


    reservas_aprobadas_percent = (reservas_aprobadas_mes / reservas_mes) * 100 if reservas_mes > 0 else 0
    reservas_pendientes_percent = (reservas_pendientes_mes / reservas_mes) * 100 if reservas_mes > 0 else 0
    reservas_rechazadas_percent = (reservas_rechazadas_mes / reservas_mes) * 100 if reservas_mes > 0 else 0
    usuarios = Usuario.objects.count()

    proximas_reservas = Reserva.objects.filter(estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA], fecha_uso__gte=datetime.now()).order_by('fecha_uso','hora_inicio')[:4]
    

    cards = [
        {'title': 'Reservas Aprobadas', 'value': reservas_aprobadas, 'icon': 'reserva', 'color': 'text-success'},
        {'title': 'Reservas Pendientes', 'value': reservas_pendientes, 'icon': 'reserva', 'color': 'text-warning'},
        {'title': 'Reservas Rechazadas', 'value': reservas_rechazadas, 'icon': 'reserva', 'color': 'text-error'},
        {'title': 'Espacios Disponibles', 'value': espacios_disponibles, 'icon': 'espacio', 'color': 'text-success'},
        {'title': 'Espacios No Disponibles', 'value': espacios_no_disponibles, 'icon': 'espacio', 'color': 'text-error'},
        {'title': 'Usuarios Registrados', 'value': usuarios, 'icon': 'usuario', 'color': 'text-info'},
    ]

    month_summary = {
        'total': reservas_mes,
        'items': [
            {'title': 'Reservas Aprobadas', 'value': floor(reservas_aprobadas_percent), 'count': reservas_aprobadas_mes, 'color': 'success'},
            {'title': 'Reservas Pendientes', 'value': floor(reservas_pendientes_percent), 'count': reservas_pendientes_mes, 'color': 'warning'},
            {'title': 'Reservas Rechazadas', 'value': floor(reservas_rechazadas_percent), 'count': reservas_rechazadas_mes, 'color': 'error'},
        ]
    }

    reservas_stats = {
        'cards': cards,
        'today': datetime.now(),
        'month_summary': month_summary,
        'proximas_reservas': proximas_reservas,
    }

    return reservas_stats
    
    
def get_stats_usuario(request):
    month = datetime.now().month
    year = datetime.now().year
    reservas_pendientes = Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE, usuario=request.user).count()
    reservas_aprobadas = Reserva.objects.filter(estado=Reserva.Estado.APROBADA, usuario=request.user).count()
    reservas_rechazadas = Reserva.objects.filter(estado=Reserva.Estado.RECHAZADA, usuario=request.user).count()

    reservas_mes = Reserva.objects.filter(usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_aprobadas_mes = Reserva.objects.filter(estado=Reserva.Estado.APROBADA, usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_pendientes_mes = Reserva.objects.filter(estado='pendiente', usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_rechazadas_mes = Reserva.objects.filter(estado='rechazada', usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()


    reservas_aprobadas_percent = (reservas_aprobadas_mes / reservas_mes) * 100 if reservas_mes > 0 else 0
    reservas_pendientes_percent = (reservas_pendientes_mes / reservas_mes) * 100 if reservas_mes > 0 else 0
    reservas_rechazadas_percent = (reservas_rechazadas_mes / reservas_mes) * 100 if reservas_mes > 0 else 0


    proximas_reservas = Reserva.objects.filter(usuario=request.user, estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA], fecha_uso__gte=datetime.now()).order_by('fecha_uso', 'hora_inicio')[:4]
    cards = [
        {'title': 'Mis Reservas Aprobadas', 'value': reservas_aprobadas, 'icon': 'reserva', 'color': 'text-success'},
        {'title': 'Mis Reservas Pendientes', 'value': reservas_pendientes, 'icon': 'reserva', 'color': 'text-warning'},
        {'title': 'Mis Reservas Rechazadas', 'value': reservas_rechazadas, 'icon': 'reserva', 'color': 'text-error'},
    ]

    month_summary = {
        'total': reservas_mes,
        'items': [
            {'title': 'Reservas Aprobadas', 'value': floor(reservas_aprobadas_percent), 'count': reservas_aprobadas_mes, 'color': 'success'},
            {'title': 'Reservas Pendientes', 'value': floor(reservas_pendientes_percent), 'count': reservas_pendientes_mes, 'color': 'warning'},
            {'title': 'Reservas Rechazadas', 'value': floor(reservas_rechazadas_percent), 'count': reservas_rechazadas_mes, 'color': 'error'},
        ]
    }

    reservas_stats = {
        'cards': cards,
        'month_summary': month_summary,
        'proximas_reservas': proximas_reservas,
    }

    return reservas_stats   


def get_stats_moderador(request):
    
    month = datetime.now().month
    year = datetime.now().year

    reservas_pendientes = Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE, espacio__ubicacion=request.user.ubicacion, espacio__piso=request.user.piso).count()
    reservas_aprobadas = Reserva.objects.filter(estado=Reserva.Estado.APROBADA, aprobado_por=request.user).count()
    reservas_rechazadas = Reserva.objects.filter(estado=Reserva.Estado.RECHAZADA, aprobado_por=request.user).count()
    
    reservas_mes = Reserva.objects.filter(espacio__ubicacion=request.user.ubicacion, espacio__piso=request.user.piso, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_aprobadas_mes = Reserva.objects.filter(estado=Reserva.Estado.APROBADA, aprobado_por=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_rechazadas_mes = Reserva.objects.filter(estado=Reserva.Estado.RECHAZADA, aprobado_por=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_pendientes_mes = Reserva.objects.filter(estado=Reserva.Estado.PENDIENTE, fecha_uso__month=month, fecha_uso__year=year).count()

    reservas_aprobadas_percent = (reservas_aprobadas_mes / reservas_mes) * 100 if reservas_mes > 0 else 0
    reservas_pendientes_percent = (reservas_pendientes_mes / reservas_mes) * 100 if reservas_mes > 0 else 0
    reservas_rechazadas_percent = (reservas_rechazadas_mes / reservas_mes) * 100 if reservas_mes > 0 else 0

    proximas_reservas = Reserva.objects.filter(espacio__ubicacion=request.user.ubicacion, espacio__piso=request.user.piso, estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA], fecha_uso__gte=datetime.now()).order_by('fecha_uso', 'hora_inicio')[:4]

    cards = [
        {'title': 'Reservas Aprobadas', 'value': reservas_aprobadas, 'icon': 'reserva', 'color': 'text-success'},
        {'title': 'Reservas Pendientes', 'value': reservas_pendientes, 'icon': 'reserva', 'color': 'text-warning'},
        {'title': 'Reservas Rechazadas', 'value': reservas_rechazadas, 'icon': 'reserva', 'color': 'text-error'},
    ]

    month_summary = {
        'total': reservas_mes,
        'items': [
            {'title': 'Reservas Aprobadas', 'value': floor(reservas_aprobadas_percent), 'count': reservas_aprobadas_mes, 'color': 'success'},
            {'title': 'Reservas Pendientes', 'value': floor(reservas_pendientes_percent), 'count': reservas_pendientes_mes, 'color': 'warning'},
            {'title': 'Reservas Rechazadas', 'value': floor(reservas_rechazadas_percent), 'count': reservas_rechazadas_mes, 'color': 'error'},
        ]
    }

    reservas_stats = {
        'cards': cards,
        'month_summary': month_summary,
        'proximas_reservas': proximas_reservas,
    }

    return reservas_stats