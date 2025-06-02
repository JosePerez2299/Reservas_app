"""
Views para los usuarios

* UsuarioListView: Muestra una lista de usuarios con un formulario de filtrado
* UsuarioCreateView: Crea un nuevo usuario
* UsuarioUpdateView: Edita un usuario existente
* UsuarioDetailView: Muestra los detalles de un usuario
* UsuarioDeleteView: Elimina un usuario existente

"""

from django.views import View
from django_filters.views import FilterView
from reservas.library.forms.usuarios import UsuarioCreateForm, UsuarioUpdateForm
from reservas.library.mixins.helpers import AjaxFormMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from reservas.models import Usuario
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Case, When, Value, CharField, Q
from django.db.models.functions import Lower, Coalesce
from reservas.library.filters.usuarios import UsuarioFilter
from reservas.resources import UsuarioResource
from django.http import HttpResponse
from datetime import datetime
import pandas as pd

class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    """
    Muestra una lista de usuarios con un formulario de filtrado
    """
    model = Usuario
    permission_required = 'reservas.view_usuario'
    template_name = 'reservas/table_view.html'
    paginate_by = 10
    filterset_class = UsuarioFilter
    
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model'] = self.model.__name__.lower()
        ctx['create_url'] = 'usuario_create'
        ctx['view_url'] = 'usuario_view'
        ctx['edit_url'] = 'usuario_edit'
        ctx['delete_url'] = 'usuario_delete'      
        
        # Definir las columnas que se mostrarán en la tabla
        ctx['cols'] = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'ubicacion': 'Ubicación',
            'piso': 'Piso',
            'group_name': 'Grupo',
        }
        return ctx

    def get_ordering(self):
        # Retornamos None para que django-filter no interfiera
        # El ordenamiento lo manejamos en get_queryset()
        return None

class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, CreateView):
    """
    Crea un nuevo usuario
    """
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('usuario')
    permission_required = 'reservas.add_usuario'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Crear Usuario',
            'url': reverse_lazy('usuario_create'),
        })
        return ctx


class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, UpdateView):
    """
    Edita un usuario existente
    """
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('usuario')
    permission_required = 'reservas.change_usuario'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': f'Editar {self.model.__name__.capitalize()}',
            'url': reverse_lazy('usuario_edit', args=[self.object.pk]),
        })
        return ctx


class UsuarioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Muestra los detalles de un usuario
    """
    model = Usuario 
    template_name = 'reservas/view.html'
    permission_required = 'reservas.view_usuario'


class UsuarioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Elimina un usuario existente
    """
    model = Usuario
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('usuario') 
    permission_required = 'reservas.delete_usuario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'url': reverse_lazy('usuario_delete', args=[self.object.pk]),
            'title': f'Eliminar {self.object.pk}'
        })
        return context

class UsuarioExportExcel(View):
    def get(self, request, *args, **kwargs):
        # Filtra o adapta tu QuerySet según necesidad. Aquí obj obtendrá todas las usuarios.
        queryset =  Usuario.objects.all()

        # Instancia el Resource y conviértelo a formato csv
        df = pd.DataFrame(list(queryset))
        # Construimos la respuesta HTTP con el contenido csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="usuarios_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv"'

        df.to_csv(response, index=False)
        return response