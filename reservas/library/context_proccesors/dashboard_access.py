from django.conf import settings


def dashboard_access(request):
    if not request.user.is_authenticated:
        return {"allowed_models": [
            ("Login", "login"),]
            }

    grupos = request.user.groups.values_list("name", flat=True)
    grupo = grupos[0] if grupos else "usuario"
    modelos = settings.DASHBOARD_ACCESS[grupo]

    return {"group": grupo, "allowed_models": modelos}
