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
from reservas.library.mixins.helpers import *
from django.urls import reverse_lazy
from reservas.library.forms.espacios import EspacioCreateForm
from django.db.models.functions import Lower

class EspacioListView(LoginRequiredMixin, ListContextMixin, SmartOrderingMixin, ExportMixin, PermissionRequiredMixin, FilterView):
    """
    Muestra una lista de espacios con un formulario de filtrado
    """
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'reservas/table_view.html'
    paginate_by = 10
    filterset_class = EspacioFilter

    cols = {
        'id': 'ID',
        'nombre': 'Nombre',
        'tipo': 'Tipo',
        'capacidad': 'Capacidad',
        'ubicacion': 'Ubicación',
        'piso': 'Piso',
        'disponible': 'Disponible',
    }

    crud_urls = {
        'create': 'espacio_create',
        'view': 'espacio_view',
        'edit': 'espacio_edit', 
        'delete': 'espacio_delete',
    }
    

class EspacioCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, FormContextMixin, CreateView):
    """
    Crea un nuevo espacio
    """
    model = Espacio
    form_class = EspacioCreateForm
    permission_required = 'reservas.add_espacio'
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('espacio')
    html_title = 'Crear Espacio'
    url = 'espacio_create'


class EspacioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, FormContextMixin, UpdateView):
    """
    Edita un espacio existente
    """
    model = Espacio
    permission_required = 'reservas.change_espacio'
    form_class = EspacioCreateForm
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('espacio')
    html_title = 'Editar Espacio'
    url = 'espacio_edit'


class EspacioDetailView(LoginRequiredMixin, PermissionRequiredMixin, FormContextMixin, DetailView):
    """
    Muestra los detalles de un espacio
    """
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'reservas/view.html'
    html_title = 'Detalles de Espacio'
    url = 'espacio_view'

class EspacioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, FormContextMixin, DeleteView):
    """
    Elimina un espacio existente
    """
    model = Espacio
    permission_required = 'reservas.delete_espacio'
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('espacio') 
    html_title = 'Eliminar Espacio'
    url = 'espacio_delete'
