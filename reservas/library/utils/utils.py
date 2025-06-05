from django.contrib.auth.models import Group
from django.utils.text import capfirst  
from django.apps import apps
from reservas.models import *
from django.utils.html import mark_safe
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
    if request.user.is_admin:
        return get_stats_administrador(request)
    elif request.user.is_usuario:
        return get_stats_usuario(request)
    elif request.user.is_moderador:
        return get_stats_moderador(request)
    return {'cards': [], 'month_summary': []}

def get_stats_administrador(request):
    month = datetime.now().month
    year = datetime.now().year
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    reservas_aprobadas = Reserva.objects.filter(estado='aprobada').count()
    reservas_rechazadas = Reserva.objects.filter(estado='rechazada').count()
    espacios_disponibles = Espacio.objects.filter(disponible=True).count()
    espacios_no_disponibles = Espacio.objects.filter(disponible=False).count()

    reservas_mes = Reserva.objects.filter(fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_aprobadas_mes = Reserva.objects.filter(estado='aprobada', fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_pendientes_mes = Reserva.objects.filter(estado='pendiente', fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_rechazadas_mes = Reserva.objects.filter(estado='rechazada', fecha_uso__month=month, fecha_uso__year=year).count()


    reservas_aprobadas_percent = (reservas_aprobadas_mes / reservas_mes) * 100
    reservas_pendientes_percent = (reservas_pendientes_mes / reservas_mes) * 100
    reservas_rechazadas_percent = (reservas_rechazadas_mes / reservas_mes) * 100
    usuarios = Usuario.objects.count()

    cards = [
        {'title': 'Reservas Aprobadas', 'value': reservas_aprobadas, 'icon': 'success', 'color': 'text-success'},
        {'title': 'Reservas Pendientes', 'value': reservas_pendientes, 'icon': 'warning', 'color': 'text-warning'},
        {'title': 'Reservas Rechazadas', 'value': reservas_rechazadas, 'icon': 'error', 'color': 'text-error'},
        {'title': 'Espacios Disponibles', 'value': espacios_disponibles, 'icon': 'success', 'color': 'text-success'},
        {'title': 'Espacios No Disponibles', 'value': espacios_no_disponibles, 'icon': 'error', 'color': 'text-error'},
        {'title': 'Usuarios Registrados', 'value': usuarios, 'icon': 'info', 'color': 'text-info'},
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
    }

    return reservas_stats
    
    
def get_stats_usuario(request):
    month = datetime.now().month
    year = datetime.now().year
    reservas_pendientes = Reserva.objects.filter(estado='pendiente', usuario=request.user).count()
    reservas_aprobadas = Reserva.objects.filter(estado='aprobada', usuario=request.user).count()
    reservas_rechazadas = Reserva.objects.filter(estado='rechazada', usuario=request.user).count()

    reservas_mes = Reserva.objects.filter(usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_aprobadas_mes = Reserva.objects.filter(estado='aprobada', usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_pendientes_mes = Reserva.objects.filter(estado='pendiente', usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()
    reservas_rechazadas_mes = Reserva.objects.filter(estado='rechazada', usuario=request.user, fecha_uso__month=month, fecha_uso__year=year).count()


    reservas_aprobadas_percent = (reservas_aprobadas_mes / reservas_mes) * 100
    reservas_pendientes_percent = (reservas_pendientes_mes / reservas_mes) * 100
    reservas_rechazadas_percent = (reservas_rechazadas_mes / reservas_mes) * 100

    cards = [
        {'title': 'Mis Reservas Aprobadas', 'value': reservas_aprobadas, 'icon': 'success', 'color': 'text-success'},
        {'title': 'Mis Reservas Pendientes', 'value': reservas_pendientes, 'icon': 'warning', 'color': 'text-warning'},
        {'title': 'Mis Reservas Rechazadas', 'value': reservas_rechazadas, 'icon': 'error', 'color': 'text-error'},
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
    }

    return reservas_stats   


def get_stats_moderador(request):
    return {'cards': [], 'month_summary': []}