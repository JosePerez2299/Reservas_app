from django.contrib.auth.models import Group
from django.utils.text import capfirst  
from django.apps import apps
from reservas.models import *
from django.utils.html import mark_safe

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
    return []

def get_stats_administrador(request):
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    reservas_aprobadas = Reserva.objects.filter(estado='aprobada').count()
    reservas_rechazadas = Reserva.objects.filter(estado='rechazada').count()
    espacios_disponibles = Espacio.objects.filter(disponible=True).count()
    espacios_no_disponibles = Espacio.objects.filter(disponible=False).count()
    usuarios = Usuario.objects.count()

    reservas_stats = [
        {'title': 'Reservas Aprobadas', 'value': reservas_aprobadas, 'icon': 'success', 'color': 'text-success'},
        {'title': 'Reservas Pendientes', 'value': reservas_pendientes, 'icon': 'warning', 'color': 'text-warning'},
        {'title': 'Reservas Rechazadas', 'value': reservas_rechazadas, 'icon': 'error', 'color': 'text-error'},
        {'title': 'Espacios Disponibles', 'value': espacios_disponibles, 'icon': 'success', 'color': 'text-success'},
        {'title': 'Espacios No Disponibles', 'value': espacios_no_disponibles, 'icon': 'error', 'color': 'text-error'},
        {'title': 'Usuarios Registrados', 'value': usuarios, 'icon': 'info', 'color': 'text-info'},
    ]

    return reservas_stats
    
    
def get_stats_usuario(request):
    return []


def get_stats_moderador(request):
    return []