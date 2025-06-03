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

class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, ListContextMixin, ExportMixin, FilterView ):
    """
    Muestra una lista de usuarios con un formulario de filtrado
    """
    model = Usuario
    permission_required = 'reservas.view_usuario'
    template_name = 'reservas/table_view.html'
    paginate_by = 10
    filterset_class = UsuarioFilter

        # Columnas que mostramos en la tabla HTML
    cols = {
        'username': 'Usuario',
        'email': 'Correo electrónico',
        'ubicacion__nombre': 'Ubicación',
        'piso': 'Piso',
        'group_name': 'Grupo',
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
        
        # Anotar con el nombre del grupo (excluyendo administrador)
        qs = qs.annotate(
            group_name=Coalesce(
                Case(
                    When(groups__name='usuario', then=Value('Usuario')),
                    When(groups__name='moderador', then=Value('Moderador')),
                    default=Value('Sin grupo'),
                    output_field=CharField()
                ),
                Value('Sin grupo'),
                output_field=CharField()
            )
        )
        
        # Aplicar filtros según permisos
        if self.request.user.is_admin:
            qs = qs.filter(Q(groups__name__in=['moderador', 'usuario']))
        else:
            qs = qs.filter(Q(groups__name='usuario'))
        
        # Aplicar ordenamiento aquí, después de la anotación
        ordering = self.request.GET.get('ordering')
        if ordering:
            if ordering.startswith('-'):
                field = ordering[1:]
                if field == 'group_name':
                    qs = qs.order_by('-group_name', '-id')
                else:
                    qs = qs.order_by(Lower(field).desc(), '-id')
            else:
                if ordering == 'group_name':
                    qs = qs.order_by('group_name', 'id')
                else:
                    qs = qs.order_by(Lower(ordering), 'id')
        else:
            qs = qs.order_by('id')
            
        return qs.distinct()


    def get_ordering(self):
        # Retornamos None para que django-filter no interfiera
        # El ordenamiento lo manejamos en get_queryset()
        return None

        

class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, FormContextMixin, CreateView):
    """
    Crea un nuevo usuario
    """
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('usuario')
    permission_required = 'reservas.add_usuario'
    html_title = 'Crear Usuario'
    url = 'usuario_create'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


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
    template_name = 'reservas/view.html'
    permission_required = 'reservas.view_usuario'
    html_title = 'Detalles de Usuario'
    url = 'usuario_view'


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'url': reverse_lazy('usuario_delete', args=[self.object.pk]),
            'title': f'Eliminar {self.object.pk}'
        })
        return context

