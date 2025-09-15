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
        # ejemplo estático. Reemplaza por tu lookup.

        data_dummy = {
            '150000': {
                "nombre": "Juan Pérez",
                "nom_gerencia": "Gerencia general",
                "email": "juan.perez@empresa.com",
                "nom_vicepresidencia": "Vicepresidencia general",
                "telefono": "+58 412 555 1212"
            },
            '150001': {
                "nombre": "María González",
                "nom_gerencia": "Gerencia de recursos humanos",
                "email": "maria.gonzalez@empresa.com",
                "nom_vicepresidencia": "Vicepresidencia administrativa",
                "telefono": "+58 412 555 1213"
            },
            '150002': {
                "nombre": "Carlos Rodríguez",
                "nom_gerencia": "Gerencia de tecnología",
                "email": "carlos.rodriguez@empresa.com",
                "nom_vicepresidencia": "Vicepresidencia técnica",
                "telefono": "+58 412 555 1214"
            },
            '150003': {
                "nombre": "Ana Martínez",
                "nom_gerencia": "Gerencia de finanzas",
                "email": "ana.martinez@empresa.com",
                "nom_vicepresidencia": "Vicepresidencia financiera",
                "telefono": "+58 412 555 1215"
            },
            '150004': {
                "nombre": "Luis Fernández",
                "nom_gerencia": "Gerencia de operaciones",
                "email": "luis.fernandez@empresa.com",
                "nom_vicepresidencia": "Vicepresidencia operativa",
                "telefono": "+58 412 555 1216"
            }
        }

        data = data_dummy.get(p00)


        if not data:
            return JsonResponse({
                'error': True,
                'message': f'Usuario con código P00 {p00} no encontrado',
                'code': 'USER_NOT_FOUND'
            }, status=404)

        return JsonResponse(data)

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
