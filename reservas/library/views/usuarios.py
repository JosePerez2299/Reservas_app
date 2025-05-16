
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from reservas.library.forms.auth import User
from django.contrib.messages.views import SuccessMessageMixin
from reservas.library.mixins.list_helpers import AutoFilterMixin, ColumnsMixin

class UsuarioListView(PermissionRequiredMixin, AutoFilterMixin, ColumnsMixin, ListView):
    model = User
    permission_required = 'reservas.view_usuario'
    template_name = 'table_view.html'
    paginate_by = 10

    list_display = [
        ('username', 'Usuario'),       
        ('first_name', 'Nombre'),        
    ]

    def get_queryset(self):
        return User.objects.filter(groups__name__in=['moderador', 'usuario']).distinct()


# TO DO todo lo de abajo :D
class UsuarioCreateView(SuccessMessageMixin, CreateView):
    model = User
    template_name = 'create.html'
    fields = ['nombre', 'ubicacion', 'capacidad', 'tipo']
    success_url = reverse_lazy('usuario')
    success_message = "¡El espacio fue creado con éxito!"

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error al crear el espacio. Por favor, verifica los datos.")
        return super().form_invalid(form)


class UsuarioUpdateView(UpdateView):
    model = User
    fields = ['nombre', 'ubicacion', 'capacidad', 'tipo', 'disponible']
    template_name = 'update.html'  # plantilla parcial
    context_object_name = 'espacio'

    def get_success_url(self):
        return reverse_lazy('usuario')
    
class UsuarioDeleteView(DeleteView):
    model = User
    template_name = 'delete.html'
    context_object_name = 'espacio'
    success_url = reverse_lazy('usuario')

    def delete(self, request, *args, **kwargs):
        """
        Override para añadir mensaje antes de redirigir.
        """
        obj = self.get_object()
        messages.success(request, f"El espacio “{obj.nombre}” fue eliminado con éxito.")
        return super().delete(request, *args, **kwargs)