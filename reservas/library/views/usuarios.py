"""
Views para los usuarios

* UsuarioListView: Muestra una lista de usuarios con un formulario de filtrado
* UsuarioCreateView: Crea un nuevo usuario
* UsuarioUpdateView: Edita un usuario existente
* UsuarioDetailView: Muestra los detalles de un usuario
* UsuarioDeleteView: Elimina un usuario existente

"""

from django_filters.views import FilterView
from reservas.library.forms.usuarios import UsuarioCreateForm, UsuarioUpdateForm
from reservas.library.mixins.helpers import *
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from reservas.models import Usuario
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Case, When, Value, CharField, Q
from django.db.models.functions import Lower, Coalesce
from reservas.library.filters.usuarios import UsuarioFilter
from django.conf import settings

class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, SmartOrderingMixin, ListCrudMixin, FilterView ):
    """
    Muestra una lista de usuarios con un formulario de filtrado
    """
    model = Usuario
    permission_required = 'reservas.view_usuario'
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

        if self.request.user.is_admin:
            qs = qs.filter(Q(groups__name__in=[settings.GRUPOS.MODERADOR, settings.GRUPOS.USUARIO]))
        elif self.request.user.is_moderador:
            qs = qs.filter(Q(groups__name=settings.GRUPOS.USUARIO))
        
        return qs


class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, CreateView):
    """
    Crea un nuevo usuario
    """
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'reservas/usuarios_create.html'
    success_url = reverse_lazy('usuario')
    permission_required = 'reservas.add_usuario'
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
    


class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, FormContextMixin, UpdateView):
    """
    Edita un usuario existente
    """
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('usuario')
    permission_required = 'reservas.change_usuario'
    html_title = 'Editar Usuario'
    url = 'usuario_edit'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class UsuarioDetailView(LoginRequiredMixin, PermissionRequiredMixin, FormContextMixin, DetailView):
    """
    Muestra los detalles de un usuario
    """
    model = Usuario 
    template_name = 'reservas/usuario_detail.html'
    permission_required = 'reservas.view_usuario'
    html_title = 'Detalles de Usuario'
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


class UsuarioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, FormContextMixin, DeleteView):
    """
    Elimina un usuario existente
    """
    model = Usuario
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('usuario') 
    permission_required = 'reservas.delete_usuario'
    html_title = 'Eliminar Usuario'
    url = 'usuario_delete'


