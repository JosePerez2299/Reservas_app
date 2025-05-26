from django.contrib.auth.models import Group
from django.utils.text import capfirst
from django.apps import apps

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