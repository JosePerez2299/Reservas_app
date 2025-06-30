# templatetags/table_actions.py
from django import template
from django.conf import settings
from reservas.models import Reserva, Usuario, Espacio

register = template.Library()


# Esta etiqueta de template solo se utiliza para renderizar los botones
# para editar o eliminar un objeto. La logica de permisos se maneja en
# el backend, por lo que no se verifica permisos en este punto.
# La razón de no verificar permisos en este punto es que se quieren
# mostrar los botones de editar y eliminar en la tabla de objetos,
# pero no se quieren habilitar para usuarios que no tengan permisos.
# En su lugar, se dejan deshabilitados, y se verifica el permiso en
# el view de edicion o eliminacion.
@register.simple_tag
def puede_editar(objeto):

    return (
        isinstance(objeto, Reserva) and objeto.estado == 'pendiente') or \
        isinstance(objeto, Usuario) or \
        isinstance(objeto, Espacio)


@register.simple_tag
def puede_eliminar(objeto):
    return (
        isinstance(objeto, Reserva) and objeto.estado == 'pendiente') or \
        isinstance(objeto, Usuario) or \
        isinstance(objeto, Espacio)

@register.simple_tag(takes_context=True)
def puede_aprobar(context, objeto):

    user = context['user']

    if not isinstance(objeto, Reserva):
        return False

    reserva = objeto

    if user.is_admin and reserva.estado == 'pendiente':
        return True

    if user.is_moderador:
        return (
            reserva.estado == 'pendiente' and 
            reserva.espacio.piso == user.piso and 
            reserva.espacio.ubicacion == user.ubicacion
            )
    return False
