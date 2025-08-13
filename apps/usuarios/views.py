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
from .forms import UsuarioCreateForm, UsuarioUpdateForm
from library.mixins.helpers import *
from django.urls import reverse, reverse_lazy
from apps.reservas.models import Usuario
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Case, When, Value, CharField, Q
from django.db.models.functions import Lower, Coalesce
from .filters import UsuarioFilter
from django.conf import settings

def custom_404_view(request, exception=None):
    """Custom 404 handler that redirects to login page."""
    return redirect(reverse('login'))

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

class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, SmartOrderingMixin, ListCrudMixin, FilterView ):
    """
    Muestra una lista de usuarios con un formulario de filtrado
    """
    model = Usuario
    permission_required = 'usuarios.view_usuario'
    template_name = 'reservas/usuarios_table.html'
    paginate_by = 10
    filterset_class = UsuarioFilter 
    can_export = True

    # Columnas que mostramos en la tabla HTML
    cols = {
        'pk': 'ID',
        'username': 'Usuario',
        'ubicacion': 'Ubicación',
        'piso': 'Piso',
        'group': 'Grupo',

    }
    
    property_to_field_mapping = {
    'group': 'groups'
    }

    # Es importante el nombre (key) que sean los definidos, para que el template pueda usarlos. 
    # El value debe ser el nombre de la url que se define en urls.py
    crud_urls = {
        'create': 'usuario_create',
        'view': 'usuario_view',
        'edit': 'usuario_edit',
        'delete': 'usuario_delete',
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Aplicar filtros según permisos

        qs = qs.annotate(
            group=Case(
                When(groups__name=settings.GRUPOS.MODERADOR, then=Value(settings.GRUPOS.MODERADOR)),
                When(groups__name=settings.GRUPOS.USUARIO, then=Value(settings.GRUPOS.USUARIO)),
                default=Value('-'),
                output_field=CharField()
            )
        )

        qs = qs.filter(qs_condiciones(self.request.user))
        return qs


class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, CreateView):
    """
    Crea un nuevo usuario
    """
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'reservas/usuarios_create.html'
    success_url = reverse_lazy('usuarios')
    permission_required = 'usuarios.add_usuario'
    url = 'usuario_create'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url'] = reverse_lazy('usuario_create')
        ctx['title'] = 'Crear Usuario'
        ctx['subtitle'] = 'Información del usuario'
        return ctx
    

class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, UpdateView):
    """
    Edita un usuario existente
    """
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'reservas/usuarios_edit.html'
    success_url = reverse_lazy('usuario')
    permission_required = 'usuarios.change_usuario'
    html_title = 'Editar Usuario'
    url = 'usuario_edit'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url'] = reverse_lazy('usuario_edit', args=[self.object.pk])
        ctx['title'] = 'Editar Usuario'
        ctx['subtitle'] = 'Información del usuario'
        return ctx
    

class UsuarioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Muestra los detalles de un usuario  
    """
    model = Usuario 
    template_name = 'reservas/usuario_detail.html'
    permission_required = 'usuarios.view_usuario'
    url = 'usuario_view'


    def get_context_data(self, **kwargs):
        reservas_aprobadas = self.object.reservas.filter(estado='aprobada').count()
        reservas_pendientes = self.object.reservas.filter(estado='pendiente').count()
        reservas_rechazadas = self.object.reservas.filter(estado='rechazada').count()
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'reservas_aprobadas': reservas_aprobadas,
            'reservas_pendientes': reservas_pendientes,
            'reservas_rechazadas': reservas_rechazadas,
        })  
        return ctx

    def get_queryset(self):
        return super().get_queryset().filter(qs_condiciones(self.request.user))


class UsuarioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, AjaxDeleteMixin, DeleteView):
    """
    Elimina un usuario existente
    """
    model = Usuario
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('usuario') 
    permission_required = 'usuarios.delete_usuario'
    url = 'usuario_delete'

    details = [ 
        {'label': 'Username', 'value': 'username'},
        {'label': 'Email', 'value': 'email'},
        {'label': 'Ubicación', 'value': 'ubicacion'},
        {'label': 'Piso', 'value': 'piso'},
        {'label': 'Grupo', 'value': 'grupo'},
    ]

    def delete(self, request, *args, **kwargs):
        if self.object.grupo == settings.GRUPOS.ADMIN:
            return JsonResponse({'error': 'No puedes eliminar un usuario con grupo ADMIN'}, status=403)
       
        if self.request.user.is_moderador and self.object.grupo != settings.GRUPOS.USUARIO:
            return JsonResponse({'error': 'Solo puedes eliminar un usuario con grupo USUARIO'}, status=403)
        elif self.request.user.is_admin and self.object.grupo != settings.GRUPOS.ADMIN:
            return JsonResponse({'error': 'Solo puedes eliminar un usuario con grupo ADMIN'}, status=403)
        else:
            return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(qs_condiciones(self.request.user))

class ProfileView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'reservas/profile.html'
    permission_required = 'usuarios.view_usuario'
    url = 'profile'

    def get_object(self):
        return self.request.user
