from django.conf import settings


def dashboard_access(request):
    # Obtener la ruta actual
    current_path = request.path_info
    current_section = current_path.strip('/').split('/')[0] if current_path != '/' else 'dashboard'
    if (request.user.is_superuser):
        grupo = settings.GRUPOS.ADMINISTRADOR
    else:
    # Obtener nombre de grupo
        grupos = request.user.groups.values_list("name", flat=True)
        grupo = request.user.groups.first().name if request.user.groups.exists() else settings.GRUPOS.USUARIO
        # Si es superusuario, mostrar todos los modelos
    
    # Permisos por modelo para este grupo
    modelos = settings.DASHBOARD_ACCESS.get(grupo, [])

    navlinks = [{"label": "Inicio", "url": "dashboard"},{"label": "Calendario", "url": "calendario"}]
    navlinks.extend([modelo['model'] for modelo in modelos if modelo['model']['name'] != 'auditlog.LogEntry'])

    print(navlinks)
    return {
        "group": grupo,
        "current_section": current_section,  # Sección actual para resaltar en el menú
        "dashboard_access": navlinks
    }
