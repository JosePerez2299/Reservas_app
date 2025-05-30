# templatetags/permisos.py
from django import template
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
def puede_editar(objeto, user, model):

    if model == 'reserva':
        return objeto.estado == 'pendiente'

    elif model == 'usuario' or model == 'Usuario':
        return True


    elif model == 'espacio':
        return True
        
    else:
        return False

@register.simple_tag
def puede_eliminar(objeto, user, model):
    if model == 'reserva':
        return objeto.estado == 'pendiente'
    elif model == 'usuario':
        return user.is_admin
    elif model== 'espacio':
        return True
        
