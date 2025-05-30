# templatetags/permisos.py
from django import template
register = template.Library()

@register.simple_tag
def puede_editar(objeto, user):
    return (
        (  user.is_admin
            or
            user.is_moderador)
        and objeto.estado == 'pendiente'
    )

@register.simple_tag
def puede_eliminar(objeto, user):
    return (
        (  user.is_admin
            or
            user.is_moderador)
        and objeto.estado == 'pendiente'
    )
    
