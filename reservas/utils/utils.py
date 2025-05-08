from django.contrib.auth.models import Group
from django.utils.text import capfirst


def get_access(user):
    """
    Recupera un conjunto de nombres de modelos (con la primera letra en mayúscula y en plural) 
    a los que el usuario tiene acceso basado en los permisos de sus grupos.

    Argumentos:
        user (User): Una instancia de usuario de Django cuyos permisos de grupo serán evaluados.

    Retorna:
        set: Un conjunto de cadenas que representan los nombres de los modelos 
        (con la primera letra en mayúscula y en plural) a los que el usuario tiene acceso.
    """



    models = set()
    for grupo in user.groups.all():
        for permiso in grupo.permissions.all():
            modelo = permiso.content_type.model  # nombre del modelo en minúsculas
            formatted_model = capfirst(modelo) + 's'
            models.add(formatted_model)
    return models