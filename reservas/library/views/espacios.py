from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from reservas.models import Espacio
from django.db.models.functions import Lower
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_filters.views import FilterView
from reservas.library.filters.espacio import EspacioFilter
from django.utils.translation import gettext_lazy as _
from reservas.library.forms.espacios import EspacioCreateForm
from django.db.models import F, Value
from django.db.models.functions import Lower
class EspacioListView(PermissionRequiredMixin, FilterView):
    model = Espacio
    permission_required = 'reservas.view_espacio'
    template_name = 'reservas/table_view.html'
    paginate_by = 10
    filterset_class = EspacioFilter

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model'] = self.model.__name__.lower()
        ctx['create_url'] = reverse('espacio_create')
        # Definir las columnas que se mostrarán en la tabla
        ctx['cols'] = {
            'nombre': 'Nombre',
            'capacidad': 'Capacidad',
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

     
class EspacioCreateView(PermissionRequiredMixin, CreateView):
    model = Espacio
    permission_required = 'reservas.add_espacio'
    template_name = 'reservas/create.html'
    fields = ['nombre', 'ubicacion', 'piso','capacidad', 'tipo']
    success_url = reverse_lazy('espacio')

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añade el nombre del modelo al contexto
        context['model_name'] = self.model.__name__
        return context

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al crear el espacio. Por favor, verifica los datos.")
        return super().form_invalid(form)
