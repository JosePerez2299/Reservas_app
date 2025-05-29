"""
Views para los espacios

* EspacioListView: Muestra una lista de espacios con un formulario de filtrado
* EspacioCreateView: Crea un nuevo espacio
* EspacioUpdateView: Edita un espacio existente
* EspacioDetailView: Muestra los detalles de un espacio
* EspacioDeleteView: Elimina un espacio existente

"""

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from reservas.models import Espacio
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters.views import FilterView
from reservas.library.filters.espacio import EspacioFilter
from reservas.library.mixins.helpers import AjaxFormMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from reservas.library.forms.espacios import EspacioCreateForm


class EspacioListView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    """
    Muestra una lista de espacios con un formulario de filtrado
    """
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'reservas/table_view.html'
    paginate_by = 10
    filterset_class = EspacioFilter

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model'] = self.model.__name__.lower()
        ctx['create_url'] = 'espacio_create'
        ctx['view_url'] = 'espacio_view'
        ctx['edit_url'] = 'espacio_edit'
        ctx['delete_url'] = 'espacio_delete'

        # Definir las columnas que se mostrarán en la tabla
        ctx['cols'] = {
            'nombre': 'Nombre',
            'capacidad': 'Capacidad',
            'ubicacion': 'Ubicación',
            'piso': 'Piso',
            'disponible': 'Disponible',
        }
        return ctx

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        if not ordering:
            return None
            
        # Lista de campos numéricos que deben ordenarse como enteros
        numeric_fields = ['capacidad', 'piso']
        
        # Eliminar el signo de ordenación temporalmente
        is_desc = ordering.startswith('-')
        field_name = ordering[1:] if is_desc else ordering
        
        # Aplicar el tipo de ordenación apropiado según el campo
        if field_name in numeric_fields:
            # Para campos numéricos, ordenar como enteros
            order_field = field_name
        else:
            # Para campos de texto, ordenar sin distinguir mayúsculas/minúsculas
            order_field = f'lower({field_name})'
        
        # Aplicar orden descendente si es necesario
        if is_desc:
            order_field = f'-{order_field}'
            
        return [order_field]


class EspacioCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, CreateView):
    """
    Crea un nuevo espacio
    """
    model = Espacio
    form_class = EspacioCreateForm
    permission_required = 'reservas.add_espacio'
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('espacio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Crear Espacio',
            'url': reverse_lazy('espacio_create'),
        })
        return ctx


class EspacioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, UpdateView):
    """
    Edita un espacio existente
    """
    model = Espacio
    permission_required = 'reservas.change_espacio'
    fields = '__all__'
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('espacio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': f'Editar {self.model.__name__.capitalize()}',
            'url': reverse_lazy('espacio_edit', args=[self.object.pk]),
        })
        return ctx


class EspacioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Muestra los detalles de un espacio
    """
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'reservas/view.html'


class EspacioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Elimina un espacio existente
    """
    model = Espacio
    permission_required = 'reservas.delete_espacio'
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('espacio') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'url': reverse_lazy('espacio_delete', args=[self.object.pk]),
            'title': f'Eliminar {self.object.nombre}'
        })
        return context
