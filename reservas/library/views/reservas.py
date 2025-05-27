"""
Views para los espacios

* EspacioListView: Muestra una lista de espacios con un formulario de filtrado
* EspacioCreateView: Crea un nuevo espacio
* EspacioUpdateView: Edita un espacio existente
* EspacioDetailView: Muestra los detalles de un espacio
* EspacioDeleteView: Elimina un espacio existente

"""

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from reservas.models import Reserva, Ubicacion
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_filters.views import FilterView
from reservas.library.mixins.helpers import AjaxFormMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from reservas.library.utils.utils import get_all_cols
from reservas.library.filters.reservas import ReservaFilter
from reservas.library.forms.reservas import ReservaCreateForm, ReservaUpdateForm
from django.db.models import Q

class ReservaListView(PermissionRequiredMixin, FilterView):
    """
    Muestra una lista de espacios con un formulario de filtrado
    """
    model = Reserva
    permission_required = 'reservas.view_reserva'
    template_name = 'reservas/table_view.html'
    paginate_by = 10
    filterset_class = ReservaFilter 


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model'] = self.model.__name__.lower()
        ctx['create_url'] = 'reserva_create'
        ctx['view_url'] = 'reserva_view'
        ctx['edit_url'] = 'reserva_edit'
        ctx['delete_url'] = 'reserva_delete'      
        
        # Definir las columnas que se mostrarán en la tabla
        ctx['cols'] = {
            'usuario': 'Usuario',
            'espacio': 'Espacio',
            'espacio__ubicacion': 'Ubicación',
            'espacio__piso': 'Piso',
            'fecha_uso': 'Fecha de uso',
            'hora_inicio': 'Hora de inicio',
            'hora_fin': 'Hora de fin',
            'estado': 'Estado',
        }   
        return ctx


    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin:
            return qs
        elif self.request.user.is_moderador:
            return qs.filter(
                Q(aprobado_por=self.request.user) | 
                (Q(espacio__ubicacion=self.request.user.ubicacion)  & 
                Q(espacio__piso=self.request.user.piso))
            )
        elif self.request.user.is_usuario:
            return qs.filter(Q(usuario=self.request.user))
        return qs.none()
    
    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        if ordering:
            if ordering.startswith('-'):
                return [Lower(ordering[1:]).desc()]
            else:
                return [Lower(ordering)]


class ReservaCreateView(AjaxFormMixin, CreateView):
    """
    Crea una nueva reserva
    """
    model = Reserva
    form_class = ReservaCreateForm
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('reserva')

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': 'Crear Reserva',
            'url': reverse_lazy('reserva_create'),
        })
        return ctx
        


class ReservaUpdateView(AjaxFormMixin, UpdateView):
    """
    Edita una reserva existente
    """
    model = Reserva
    form_class = ReservaUpdateForm  
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('reserva')

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': f'Editar {self.model.__name__.capitalize()}',
            'url': reverse_lazy('reserva_edit', args=[self.object.pk]),
        })
        return ctx


class ReservaDetailView(DetailView):
    """
    Muestra los detalles de un espacio
    """
    model = Reserva
    template_name = 'reservas/reservas_detail.html'


class ReservaDeleteView(DeleteView):
    """
    Elimina un espacio existente
    """
    model = Reserva
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('reserva') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'url': reverse_lazy('reserva_delete', args=[self.object.pk]),   
            'title': f'Eliminar Reserva {self.object.pk}'
        })
        return context
