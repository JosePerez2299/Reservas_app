from django.conf import settings


def dashboard_access(request):
    # Obtener la ruta actual
    current_path = request.path_info
    current_section = current_path.strip('/').split('/')[0] if current_path != '/' else 'dashboard'
    
    # Obtener nombre de grupo
    grupos = request.user.groups.values_list("name", flat=True)
    grupo = grupos[0] if grupos else settings.GRUPOS.USUARIO
    
    # Permisos por modelo para este grupo
    permisos_por_modelo = settings.DASHBOARD_ACCESS.get(grupo, [])
    return {
        "group": grupo,
        "current_section": current_section,  # Sección actual para resaltar en el menú
        "dashboard_access": permisos_por_modelo
    }
