from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
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


# views.py


class AjaxFormMixin:
    def form_invalid(self, form):
        html = self.render_to_response(self.get_context_data(form=form)).rendered_content
        return JsonResponse({'success': False, 'html_form': html})

    def form_valid(self, form):
        # Guarda y asigna a self.object
        self.object = form.save()
        return JsonResponse({
            'success': True,
            'redirect_url': self.get_success_url()
        })

class EspacioCreateView(AjaxFormMixin, CreateView):
    model = Espacio
    form_class = EspacioCreateForm
    template_name = 'includes/ajax_form.html'
    success_url = reverse_lazy('espacio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Crear Espacio',
            'url': reverse_lazy('espacio_create'),
        })
        return ctx

class EspacioUpdateView(AjaxFormMixin, UpdateView):
    model = Espacio
    fields = '__all__'
    template_name = 'includes/ajax_form.html'
    success_url = reverse_lazy('espacio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': f'Editar {self.object.nombre}',
            'url': reverse_lazy('espacio_edit', args=[self.object.pk]),
        })
        return ctx


class EspacioDetailView(DetailView):
    model = Espacio
    template_name = 'reservas/view.html'



class EspacioDeleteView(DeleteView):
    model = Espacio
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('espacio')