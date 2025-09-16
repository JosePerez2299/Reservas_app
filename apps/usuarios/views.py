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
from apps.reservas.models import Usuario
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Case, When, Value, CharField, Q
from django.conf import settings
from django.views import View
from django.http import JsonResponse, response
from django.contrib.auth import get_user_model
import requests

User = get_user_model()

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

        payload = {'id_sap': p00}

        url = "http://161.196.39.206/talento_produccion/public/api/empleado/consultar"
        response = requests.post(url, json=payload, verify=False)

        data = response.json()

        if 'message' not in data or data['message'] != 'Empleado no existe' and data['id_sap'] != 'Debe tener 6 digitos.':

            nombres = data.get('nombres', '').strip().title()
            apellidos = data.get('apellidos', '').strip().title()
            email = data.get("email", "").strip().lower()
            telefono = data.get("tlf_celular", "")

            resultado = {
                "nombre": f"{nombres} {apellidos}".strip(),
                "nom_gerencia": data.get("posicion", {}).get("nom_posicion_reporta", ""),
                "email": email,
                "nom_vicepresidencia": data.get("posicion", {}).get("nom_posicion", ""),
                "telefono": telefono
            }

            return JsonResponse(resultado)
        else:

            return JsonResponse({
                'error': True,
                'message': f'Usuario con código P00 {p00} no encontrado',
                'code': 'USER_NOT_FOUND'
            }, status=404)



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
