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
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_filters.views import FilterView
from reservas.library.filters.espacio import EspacioFilter
from reservas.library.mixins.helpers import AjaxFormMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy


class EspacioListView(PermissionRequiredMixin, FilterView):
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
        ctx['create_url'] = reverse_lazy('espacio_create')
        
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
        if ordering:
            if ordering.startswith('-'):
                return [Lower(ordering[1:]).desc()]
            else:
                return [Lower(ordering)]
        return ['nombre']  # o lo que uses por defecto


class EspacioCreateView(AjaxFormMixin, CreateView):
    """
    Crea un nuevo espacio
    """
    model = Espacio
    fields = '__all__'
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('espacio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Crear Espacio',
            'url': reverse_lazy('espacio_create'),
        })
        return ctx


class EspacioUpdateView(AjaxFormMixin, UpdateView):
    """
    Edita un espacio existente
    """
    model = Espacio
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


class EspacioDetailView(DetailView):
    """
    Muestra los detalles de un espacio
    """
    model = Espacio
    template_name = 'reservas/view.html'


class EspacioDeleteView(DeleteView):
    """
    Elimina un espacio existente
    """
    model = Espacio
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('espacio') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'url': reverse_lazy('espacio_delete', args=[self.object.pk]),
            'title': f'Eliminar {self.object.nombre}'
        })
        return context
