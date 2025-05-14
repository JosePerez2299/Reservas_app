from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from reservas.library.mixins.list_helpers import AutoFilterMixin, ColumnsMixin
from reservas.models import Espacio
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin


class EspacioListView(PermissionRequiredMixin, AutoFilterMixin, ColumnsMixin, ListView):
    model = Espacio
    permission_required = 'reservas.change_espacio'
    template_name = 'table_view.html'
    paginate_by = 10

    list_display = [
        ('nombre', 'Nombre'),        
        ('tipo', 'Tipo'),
        ('capacidad', 'Capacidad'),
        ('disponible', 'Disponible'),
    ]

class EspacioCreateView(SuccessMessageMixin, CreateView):
    model = Espacio
    template_name = 'espacios/create.html'
    fields = ['nombre', 'ubicacion', 'capacidad', 'tipo']
    success_url = reverse_lazy('espacio_list')
    success_message = "¡El espacio fue creado con éxito!"

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al crear el espacio. Por favor, verifica los datos.")
        return super().form_invalid(form)


class EspacioUpdateView(UpdateView):
    model = Espacio
    fields = ['nombre', 'ubicacion', 'capacidad', 'tipo', 'disponible']
    template_name = 'espacios/edit.html'  # plantilla parcial
    context_object_name = 'espacio'

    def get_success_url(self):
        return reverse_lazy('espacio_list')
    
class EspacioDeleteView(DeleteView):
    model = Espacio
    template_name = 'espacios/confirm_delete.html'
    context_object_name = 'espacio'
    success_url = reverse_lazy('espacio_list')

    def delete(self, request, *args, **kwargs):
        """
        Override para añadir mensaje antes de redirigir.
        """
        obj = self.get_object()
        messages.success(request, f"El espacio “{obj.nombre}” fue eliminado con éxito.")
        return super().delete(request, *args, **kwargs)