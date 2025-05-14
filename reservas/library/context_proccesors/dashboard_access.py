from django.conf import settings


def dashboard_access(request):
    # obtener nombre de grupo
    grupos = request.user.groups.values_list("name", flat=True)
    grupo = grupos[0] if grupos else "usuario"
    # permisos por modelo para este grupo
    permisos_por_modelo = settings.DASHBOARD_ACCESS.get(grupo, {})
    return {
        "group": grupo,
        # ej. {'usuario': ['add','change',...], 'espacio': [...], ...}
        "dashboard_access": permisos_por_modelo
    }
