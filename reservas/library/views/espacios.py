from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from reservas.library.mixins.list_helpers import AutoFilterMixin, ColumnsMixin
from reservas.models import Espacio
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_filters.views import FilterView
from django.db import models
from reservas.library.filters.espacio import EspacioFilter
from django.utils.translation import gettext_lazy as _

class EspacioListView(PermissionRequiredMixin, FilterView):
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'table_view.html'
    paginate_by = 15
    filterset_class = EspacioFilter

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Definir las columnas que se mostrarán en la tabla
        ctx['cols'] = {
            'nombre': 'Nombre',
            'tipo': 'Tipo',
            'capacidad': 'Capacidad',
            'piso': 'Piso',
            'disponible': 'Disponible',
        }
        return ctx



class EspacioCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Espacio
    permission_required = 'reservas.add_espacio'
    template_name = 'create.html'
    fields = ['nombre', 'ubicacion', 'piso','capacidad', 'tipo']
    success_url = reverse_lazy('espacio')
    success_message = "¡El espacio fue creado con éxito!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añade el nombre del modelo al contexto
        context['model_name'] = self.model.__name__
        return context

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al crear el espacio. Por favor, verifica los datos.")
        return super().form_invalid(form)


class EspacioUpdateView(UpdateView):
    model = Espacio
    fields = ['nombre', 'ubicacion', 'capacidad', 'tipo', 'disponible']
    template_name = 'update.html'  # plantilla parcial
    context_object_name = 'espacio'

    def get_success_url(self):
        return reverse_lazy('espacio_list')
    
class EspacioDeleteView(DeleteView):
    model = Espacio
    template_name = 'delete.html'
    context_object_name = 'espacio'
    success_url = reverse_lazy('espacio_list')

    def delete(self, request, *args, **kwargs):
        """
        Override para añadir mensaje antes de redirigir.
        """
        obj = self.get_object()
        messages.success(request, f"El espacio “{obj.nombre}” fue eliminado con éxito.")
        return super().delete(request, *args, **kwargs)