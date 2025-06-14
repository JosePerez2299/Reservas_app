from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def get_icon(icon_name, icon_class=None):
    if icon_class is None:
        icon_class = 'w-10 h-10' 

    if icon_name not in ['success', 'error', 'warning', 'info']:
        icon_name = 'info'
    
    icons_svg = {
        'success': mark_safe(f'''<svg xmlns="http://www.w3.org/2000/svg"  fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="{icon_class}">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" />
                            </svg>
        '''),
        'error': mark_safe(f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="{icon_class}">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                            </svg>
        '''),
        'warning': mark_safe(f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="{icon_class}">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                            </svg>
        '''),
        'info': mark_safe(f'''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="{icon_class}">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
                            </svg>
        ''')
    }

    return icons_svg.get(icon_name)




@register.simple_tag()
def get_message(logEntry):
    actor = f"\"{ logEntry.actor.username}\"" if logEntry.actor else "Alguien"
    model = logEntry.content_type.model.lower()
    obj = logEntry.object_repr
    action = logEntry.action
    timestamp = logEntry.timestamp.strftime("%d/%m/%Y %H:%M:%S")
    changes = getattr(logEntry, "changes_dict", {})

    if action == 0:  # CREATE
        return f"{actor} creó {articulo(model)} {model} \"{obj}\""
    
    elif action == 1:  # UPDATE
        if model == "reserva" and "estado" in changes:
            nuevo_estado = changes["estado"][1]
            return f"{actor} {estado_verb(nuevo_estado)} la reserva \"{obj}\""
        else:
            return f"{actor} actualizó la información de {articulo(model)} {model} \"{obj}\" "

    elif action == 2:  # DELETE
        return f"{actor} eliminó {articulo(model)} {model} \"{obj}\" "

    return f"{actor} realizó una acción desconocida sobre {model} "


# Función auxiliar para poner "el" o "la"
def articulo(modelo):
    femeninos = ["reserva", "información", "actividad"]  # puedes expandir
    return "la" if modelo in femeninos else "el"

# Función auxiliar para transformar estado en verbo
def estado_verb(estado):
    estado = estado.lower()
    if estado == "aprobada":
        return "aprobó"
    elif estado == "rechazada":
        return "rechazó"
    elif estado == "pendiente":
        return "marcó como pendiente"
    return f"cambió el estado a {estado}"
