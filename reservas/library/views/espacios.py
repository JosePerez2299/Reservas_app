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
from reservas.library.forms.espacios import *
from django.db.models.functions import Lower

class EspacioListView(LoginRequiredMixin, ListCrudMixin, SmartOrderingMixin, PermissionRequiredMixin, FilterView):
    """
    Muestra una lista de espacios con un formulario de filtrado
    """
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'reservas/espacio_table.html'
    paginate_by = 10
    filterset_class = EspacioFilter
    can_export = True

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
    

class EspacioCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, CreateView):
    """
    Crea un nuevo espacio
    """
    model = Espacio
    form_class = EspacioCreateForm
    permission_required = 'reservas.add_espacio'
    template_name = 'reservas/espacios_create.html'
    success_url = reverse_lazy('espacio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Crear Espacio'
        ctx['url'] = reverse_lazy('espacio_create')
        ctx['subtitle'] = 'Información del espacio'
        return ctx


class EspacioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, UpdateView):
    """
    Edita un espacio existente
    """
    model = Espacio
    permission_required = 'reservas.change_espacio'
    form_class = EspacioUpdateForm
    template_name = 'reservas/espacios_edit.html'
    success_url = reverse_lazy('espacio')
    html_title = 'Editar Espacio'

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs   

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Editar Espacio'
        ctx['url'] = reverse_lazy('espacio_edit', args=[self.object.pk])
        ctx['subtitle'] = 'Información del espacio'
        return ctx




class EspacioDetailView(LoginRequiredMixin, PermissionRequiredMixin, FormContextMixin, DetailView):
    """
    Muestra los detalles de un espacio
    """
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'reservas/espacio_detail.html'
    html_title = 'Detalles de Espacio'
    url = 'espacio_view'

class EspacioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, AjaxDeleteMixin, DeleteView):
    """
    Elimina un espacio existente
    """
    model = Espacio
    permission_required = 'reservas.delete_espacio'
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('espacio') 
    url = 'espacio_delete'
    details = [ 
        {'label': 'Nombre', 'value': 'nombre'},
        {'label': 'Tipo', 'value': 'tipo'},
        {'label': 'Capacidad', 'value': 'capacidad'},
        {'label': 'Ubicación', 'value': 'ubicacion'},
        {'label': 'Piso', 'value': 'piso'},
        {'label': 'Disponible', 'value': 'disponible'},
    ]