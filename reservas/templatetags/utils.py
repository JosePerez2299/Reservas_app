from django import template
from django.utils.safestring import mark_safe
from django.apps import apps
from reservas.models import *
from reservas.templatetags.model_extras import get_attr
from datetime import datetime
from datetime import date
register = template.Library()

@register.simple_tag
def get_icon(icon_name):

    dict_icons = {
        'reserva': 'fas fa-calendar-alt',
        'reservas': 'fas fa-calendar-alt',
        'espacio': 'fas fa-building',
        'espacios': 'fas fa-building',
        'usuario': 'fas fa-users',
        'usuarios': 'fas fa-users',
        'log': 'fas fa-clipboard-list',
        'dashboard': 'fas fa-tachometer-alt',
        'view': 'fas fa-eye',
        'edit': 'fas fa-edit',
        'delete': 'fas fa-trash',
        'add': 'fas fa-plus',
        'search': 'fas fa-search',
        'filter': 'fas fa-filter',
        'sort': 'fas fa-sort',
    }

    icon_class = dict_icons.get(icon_name)
    if icon_class is None:
        icon_class = 'fas fa-info-circle'

    return mark_safe(f'<i class="{icon_class}"></i>')

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


@register.filter
def get_td_html(obj, field):


    attr = None

    try:
        attr = get_attr(obj, field)
    except:
        return mark_safe(f"""{str(obj)}""")
    
    if field == "group":
        print(attr)    

    if isinstance(attr, bool):
        if attr:
            return mark_safe(f"""<span class="badge badge-lg badge-success"><i class="fa-solid fa-check"></i></span>""")
        else:
            return mark_safe(f"""<span class="badge badge-lg badge-error"><i class="fa-solid fa-xmark"></i></span>""")
    
    if field == "id":
        return obj.id
    if field == "usuario" or field == "aprobado_por":


        return mark_safe(f"""      <div class="flex items-center  gap-3">
                                        <div class="avatar placeholder">
                                            <div class="bg-secondary text-secondary-content rounded-full w-8">
                                                <span class="text-xs">{(obj.usuario.username[0] + obj.usuario.username[1]).upper()}</span>
                                            </div>
                                        </div>
                                        <div class="text-start">
                                            <div class="font-bold">{obj.usuario.username}</div>
                                            <div class="text-sm opacity-50">{obj.usuario.email}</div>
                                        </div>
                                    </div>""")                            
    
    elif isinstance(obj, Reserva):

        if field == "espacio":
            max_length = 15  # Maximum characters to show before truncating
            nombre = obj.espacio.nombre
            ubicacion_nombre = obj.espacio.ubicacion.nombre
            
            # Truncate names if they're too long
            nombre_display = (nombre[:max_length] + '...') if len(nombre) > max_length else nombre
            ubicacion_display = (ubicacion_nombre[:max_length] + '...') if len(ubicacion_nombre) > max_length else ubicacion_nombre
            
            return mark_safe(f"""<div>
                <div class="font-semibold">{nombre_display}</div>
                <div class="text-sm opacity-50">
                   {ubicacion_display}
                -
                    Piso {obj.espacio.piso}
                </div>
            </div>""")
        
        elif field == "fecha_uso":
            return mark_safe(f"""   <div>
                                        <div class="font-semibold">{obj.fecha_uso.strftime("%d/%m/%Y")} </div>
                                        <div class="text-sm opacity-50">{obj.hora_inicio.strftime("%I:%M %p") } - {obj.hora_fin.strftime("%I:%M %p")}</div>
                                    </div>""")
        elif field == "aprobado_por":
            return mark_safe(f"""        <div>
                                        <div class="font-semibold">{obj.aprobado_por.username if obj.aprobado_por else "-"}</div>
                                    </div>""")

        elif field == "estado":
            
            print(obj.estado)
            estado_html = ""
            if obj.estado == Reserva.Estado.PENDIENTE:
                estado_html += "warning"
            elif obj.estado == Reserva.Estado.APROBADA:
                if (obj.fecha_uso == date.today() and obj.hora_inicio.time() < datetime.now().time() and obj.hora_fin.time() > datetime.now().time()   ):
                    return mark_safe(f""" <p class="badge  p-1 badge-lg badge-success text-base-100 ">En uso</p>""")
                else:
                    estado_html += "success"
            elif obj.estado == Reserva.Estado.RECHAZADA:
                estado_html += "error"
            return mark_safe(f""" <p class="badge  p-1 badge-lg badge-{estado_html} text-base-100 ">{obj.estado.capitalize()}</p>""")


    elif isinstance(obj, Espacio):
        if field == "nombre":
            return mark_safe(f"""   <div>
                                        <div class="font-semibold">{obj.nombre}</div>
                                        <div class="text-sm opacity-50">{obj.tipo}</div>
                                        
                                    </div>""")
        elif field == "ubicacion":
            return mark_safe(f"""   <div>
                                        <div class="font-semibold">{obj.piso}</div>
                                    </div>""")
        
    elif isinstance(obj, Usuario):
        if field == "username" or field == "email":
             return mark_safe(f"""      <div class="flex items-center  gap-3">
                                        <div class="avatar placeholder">
                                            <div class="bg-secondary text-secondary-content rounded-full w-8">
                                                <span class="text-xs">{(obj.username[0] + obj.username[1]).upper()}</span>
                                            </div>
                                        </div>
                                        <div class="text-start">
                                            <div class="font-bold">{obj.username}</div>
                                            <div class="text-sm opacity-50">{obj.email}</div>
                                        </div>
                                    </div>""")                            
    
        
        elif field == "ubicacion":
            return mark_safe(f"""   <div>
                                        <div class="font-semibold">{obj.ubicacion.nombre}</div>
                                    </div>""")
        
        elif field == "group":

            if obj.group == Usuario.GRUPOS.MODERADOR:
                return mark_safe(f"""   <div>
                                            <div class="badge badge-lg badge-success text-base-100 min-w-24  ">{obj.group.capitalize()}</div>
                                        </div>""")
            elif obj.group == settings.GRUPOS.USUARIO:
                return mark_safe(f"""   <div>
                                            <div class="badge badge-lg badge-warning text-base-100  min-w-24  ">{obj.group.capitalize()}</div>
                                        </div>""")
            else:
                return mark_safe(f"""   <div>
                                            <div class="badge badge-lg badge-error text-base-100  min-w-24  ">{obj.group.capitalize()}</div>
                                        </div>""")

        

  
    return attr


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
