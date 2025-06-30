from django.conf import settings


def dashboard_access(request):
    # Obtener la ruta actual
    current_path = request.path_info
    current_section = current_path.strip('/').split('/')[0] if current_path != '/' else 'dashboard'
    
    # Obtener nombre de grupo
    grupos = request.user.groups.values_list("name", flat=True)
    grupo = grupos[0] if grupos else settings.GRUPOS.USUARIO
    
    # Permisos por modelo para este grupo
    modelos = settings.DASHBOARD_ACCESS.get(grupo, [])
    navlinks = [{"label": "Inicio", "url": "dashboard"},{"label": "Calendario", "url": "calendario"}]
    navlinks.extend([modelo['model'] for modelo in modelos if modelo['model']['name'] != 'auditlog.LogEntry'])
    return {
        "group": grupo,
        "current_section": current_section,  # Sección actual para resaltar en el menú
        "dashboard_access": navlinks
    }
