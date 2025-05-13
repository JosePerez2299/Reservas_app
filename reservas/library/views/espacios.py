from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from reservas.models import Espacio
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Q


class EspacioListView(ListView):
    model = Espacio
    template_name = 'espacios/list.html'
    context_object_name = 'espacios'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q         = self.request.GET.get('q', '').strip()
        available = self.request.GET.get('available', 'all')
        tipo      = self.request.GET.get('tipo', 'all')
        cap_min   = self.request.GET.get('cap_min', '').strip()
        cap_max   = self.request.GET.get('cap_max', '').strip()
        sort = self.request.GET.get('sort', '')


        # Búsqueda texto
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q) |
                Q(ubicacion__icontains=q)
            )

        # Disponibilidad
        if available == 'yes':
            qs = qs.filter(disponible=True)
        elif available == 'no':
            qs = qs.filter(disponible=False)

        # Tipo de espacio
        if tipo in dict(Espacio.TIPO_CHOICES):
            qs = qs.filter(tipo=tipo)

        # Rango de capacidad
        if cap_min.isdigit():
            qs = qs.filter(capacidad__gte=int(cap_min))
        if cap_max.isdigit():
            qs = qs.filter(capacidad__lte=int(cap_max))

         # Ordenamiento
        valid_sorts = {
            'nombre': 'nombre',
            '-nombre': '-nombre',
            'capacidad': 'capacidad',
            '-capacidad': '-capacidad',
            'ubicacion': 'ubicacion',
            '-ubicacion': '-ubicacion',
        }
        if sort in valid_sorts:
            qs = qs.order_by(valid_sorts[sort])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'q':         self.request.GET.get('q', '').strip(),
            'available': self.request.GET.get('available', 'all'),
            'tipo':      self.request.GET.get('tipo', 'all'),
            'cap_min':   self.request.GET.get('cap_min', '').strip(),
            'cap_max':   self.request.GET.get('cap_max', '').strip(),
            'tipos':     Espacio.TIPO_CHOICES,
            'sort': self.request.GET.get('sort', ''),
        })
        return ctx


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