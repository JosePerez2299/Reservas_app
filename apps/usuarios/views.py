# Create your views here.
"""
Views para los usuarios

* UsuarioListView: Muestra una lista de usuarios con un formulario de filtrado
* UsuarioCreateView: Crea un nuevo usuario
* UsuarioUpdateView: Edita un usuario existente
* UsuarioDetailView: Muestra los detalles de un usuario
* UsuarioDeleteView: Elimina un usuario existente

"""

from django_filters.views import FilterView
from django.views.generic import TemplateView

from library.utils.utils import get_stats
from library.mixins.helpers import *
from django.urls import reverse, reverse_lazy
from apps.usuarios.models import Usuario
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Case, When, Value, CharField, Q
from django.conf import settings
from django.views import View
from django.http import JsonResponse, response
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
import requests
import logging
import environ

User = get_user_model()
env = environ.Env()

def custom_404_view(request, exception=None):
    """Custom 404 handler that redirects to login page."""
    return redirect(reverse('login'))


class UsuarioApiView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Muestra los detalles de un usuario
    """
    permission_required = 'usuarios.view_usuario'

    def get(self, request, *args, **kwargs):
        p00 = kwargs.get('p00')


        # Seccion de codigo y variables para debug en entorno local
        DEBUG_HOME = env.bool("DEBUG_HOME", default=False)
        if DEBUG_HOME:
            print(f"Buscando usuario con P00: {p00}")
            usuarios = Usuario.objects.filter(p00='P00'+ p00).values(
                'first_name', 'last_name', 'gerencia', 'email', 'vicepresidencia', 'telefono'
            )
            print(usuarios)
            usuario = usuarios.first()
            print(usuario)
            if usuario:
                return JsonResponse({    
                    "nombre": f"{usuario['first_name']} {usuario['last_name']}".strip(),
                    "nom_gerencia": usuario.get("gerencia", ""),
                    "email": usuario.get("email", ""),
                    "nom_vicepresidencia": usuario.get("vicepresidencia", ""),
                    "telefono": usuario.get("telefono", "")
                })

            return JsonResponse({
                    'error': True,
                    'message': 'No se pudo procesar la solicitud. Inténtalo más tarde.',
                    'code': 'MISSING_API_URL'
                }, status=500)

        # Validación temprana del P00 (6 dígitos numéricos) para evitar llamadas innecesarias
        if not p00 or not str(p00).isdigit() or len(str(p00)) != 6:
            return JsonResponse({
                'error': True,
                'message': 'El código P00 debe tener exactamente 6 dígitos numéricos.',
                'code': 'INVALID_P00_FORMAT'
            }, status=400)

        payload = {'id_sap': p00}
        # Obtener URL base directAPI_TALENTO_URLamente desde variables de entorno
        base_url = env("API_TALENTO_URL", default=None)
        if not base_url:
            logging.getLogger(__name__).error("Falta variable de entorno API_TALENTO_URL")
            return JsonResponse({
                'error': True,
                'message': 'No se pudo procesar la solicitud. Inténtalo más tarde.',
                'code': 'MISSING_API_URL'
            }, status=500)

        url = base_url.rstrip('/') + "/api/empleado/consultar"
        try:
            response = requests.post(
                url,
                json=payload,
                verify=False,
                timeout=10,
                headers={'Accept': 'application/json'}
            )
        except requests.RequestException as exc:
            logging.getLogger(__name__).error("No se pudo contactar al servicio externo: %s", exc)
            return JsonResponse({
                'error': True,
                'message': 'No se pudo procesar la solicitud. Inténtalo más tarde.',
                'code': 'UPSTREAM_UNREACHABLE'
            }, status=502)

        # Validar estado HTTP antes de intentar parsear JSON
        if response.status_code != 200:
            # Registrar cuerpo para depuración en entorno de desarrollo
            try:
                body_preview = response.text[:500]
            except Exception:
                body_preview = '<no-body>'
            logging.getLogger(__name__).error(
                "Fallo upstream %s - status=%s body=%s", url, response.status_code, body_preview
            )
            return JsonResponse({
                'error': True,
                'message': 'No se pudo procesar la solicitud. Inténtalo más tarde.',
                'code': 'UPSTREAM_BAD_STATUS'
            }, status=502)

        # Intentar parsear JSON de forma segura
        try:
            data = response.json()
        except ValueError:
            # Respuesta no es JSON válido
            logging.getLogger(__name__).error("Respuesta no válida del servicio externo (no es JSON)")
            return JsonResponse({
                'error': True,
                'message': 'No se pudo procesar la solicitud. Inténtalo más tarde.',
                'code': 'UPSTREAM_INVALID_JSON'
            }, status=502)

        if not isinstance(data, dict):
            logging.getLogger(__name__).error("Formato de respuesta inesperado del servicio externo: %s", type(data))
            return JsonResponse({
                'error': True,
                'message': 'No se pudo procesar la solicitud. Inténtalo más tarde.',
                'code': 'UPSTREAM_UNEXPECTED_FORMAT'
            }, status=502)

        # Manejo explícito de mensajes de error del proveedor
        if data.get('message') == 'Empleado no existe' or data.get('id_sap') == 'Debe tener 6 digitos.':
            return JsonResponse({
                'error': True,
                'message': f'Usuario con código P00 {p00} no encontrado',
                'code': 'USER_NOT_FOUND'
            }, status=404)

        # Extraer campos esperados
        nombres = (data.get('nombres') or '').strip().title()
        apellidos = (data.get('apellidos') or '').strip().title()
        email = (data.get('email') or '').strip().lower()
        telefono = data.get('tlf_celular') or ''
        resultado = {
            "nombre": f"{nombres} {apellidos}".strip(),
            "nom_gerencia": (data.get("posicion") or {}).get("nom_posicion_reporta", ""),
            "email": email,
            "nom_vicepresidencia": (data.get("posicion") or {}).get("nom_posicion", ""),
            "telefono": telefono
        }

        return JsonResponse(resultado)



class Dashboard(LoginRequiredMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = get_stats(self.request)
        context['stats'] = stats
        return context
    
    template_name = 'reservas/dashboard.html'

def qs_condiciones(user):
    if user.is_admin:
        return Q(groups__name__in=[settings.GRUPOS.MODERADOR, settings.GRUPOS.USUARIO])
    elif user.is_moderador:
        return Q(groups__name=settings.GRUPOS.USUARIO)
    else:
        return Q()


class ProfileView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'reservas/profile.html'
    permission_required = 'usuarios.view_usuario'
    url = 'profile'

    def get_object(self):
        return self.request.user
