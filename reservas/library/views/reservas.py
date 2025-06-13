"""
Views para las reservas

* ReservaListView: Muestra una lista de reservas con un formulario de filtrado
* ReservaCreateView: Crea una nueva reserva
* ReservaUpdateView: Edita una reserva existente
* ReservaDetailView: Muestra los detalles de una reserva
* ReservaDeleteView: Elimina una reserva existente

"""

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from reservas.models import Reserva
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters.views import FilterView
from reservas.library.mixins.helpers import *
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from reservas.library.filters.reservas import ReservaFilter
from reservas.library.forms.reservas import ReservaCreateForm, ReservaUpdateForm
from django.db.models import Q


class ReservaListView(LoginRequiredMixin, PermissionRequiredMixin, SmartOrderingMixin, ListCrudMixin, FilterView):
    """
    Muestra una lista de reservas con un formulario de filtrado
    """
    model = Reserva
    permission_required = 'reservas.view_reserva'
    template_name = 'reservas/table_view.html'
    paginate_by = 10
    can_export = True

    # Columnas que mostramos en la tabla HTML
    cols = {
        'id': 'ID',
        'usuario': 'Usuario',
        'espacio': 'Espacio',
        'fecha_uso': 'Fecha de uso',
        'estado': 'Estado',
        'aprobado_por': 'Aprobado por',
    }

    # Es importante el nombre (key) que sean los definidos, para que el template pueda usarlos. 
    # El value debe ser el nombre de la url que se define en urls.py
    crud_urls = {
        'create': 'reserva_create',
        'view': 'reserva_view',
        'edit': 'reserva_edit',
        'delete': 'reserva_delete',
    }

    # Filtros
    filterset_class = ReservaFilter 


    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin:
            return qs
        elif self.request.user.is_moderador:
            return qs.filter(
                Q(usuario=self.request.user) | 
                Q(aprobado_por=self.request.user) | 
                (Q(espacio__ubicacion=self.request.user.ubicacion)  & 
                Q(espacio__piso=self.request.user.piso))
            )
        elif self.request.user.is_usuario:
            return qs.filter(Q(usuario=self.request.user))
        return qs.none()
    
    

   
class ReservaCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, FormContextMixin, CreateView):
    """
    Crea una nueva reserva
    """
    model = Reserva
    form_class = ReservaCreateForm
    template_name = 'reservas/edit_create.html'
    success_url = reverse_lazy('reserva')
    permission_required = 'reservas.add_reserva'
    html_title = 'Crear Reserva'
    url = 'reserva_create'

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ReservaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, FormContextMixin, UpdateView ):
    """
    Edita una reserva existente
    """
    model = Reserva
    form_class = ReservaUpdateForm  
    template_name = 'reservas/reserva_edit.html'
    success_url = reverse_lazy('reserva')
    permission_required = 'reservas.change_reserva'
    html_title = 'Editar Reserva'
    url = 'reserva_edit'

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ReservaDetailView(LoginRequiredMixin, FormContextMixin, DetailView):
    """
    Muestra los detalles de una reserva
    """
    model = Reserva
    template_name = 'reservas/reservas_detail.html'
    permission_required = 'reservas.view_reserva'
    html_title = 'Detalles de Reserva'
    url = reverse_lazy('reserva_view')

class ReservaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, FormContextMixin, DeleteView):
    """
    Elimina una reserva existente
    """
    model = Reserva
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('reserva') 
    permission_required = 'reservas.delete_reserva'
    html_title = 'Eliminar Reserva'
    url = 'reserva_delete'