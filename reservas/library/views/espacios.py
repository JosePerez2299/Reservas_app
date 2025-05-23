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
from django.http import JsonResponse
from django.template.loader import render_to_string

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

    


class EspacioCreateView(CreateView):
    model = Espacio
    form_class = EspacioCreateForm
    success_url = reverse_lazy('espacio')
    template_name = 'reservas/create.html'   # Tu create.html

    def form_invalid(self, form):
        # Si viene por AJAX, devolvemos el HTML con errores (status 200)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return self.render_to_response(self.get_context_data(form=form))
        # Si no, comportamiento normal (redirecciona o renderiza full page)
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        # Si viene por AJAX, devolvemos JSON con éxito y URL de redirect
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.success_url
            })
        # Si no, comportamiento normal
        return super().form_valid(form)
