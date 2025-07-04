"""
Views para las reservas

* ReservaListView: Muestra una lista de reservas con un formulario de filtrado
* ReservaCreateView: Crea una nueva reserva
* ReservaUpdateView: Edita una reserva existente
* ReservaDetailView: Muestra los detalles de una reserva
* ReservaDeleteView: Elimina una reserva existente

"""
import json
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from reservas.models import Reserva
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters.views import FilterView
from reservas.library.mixins.helpers import *
from django.db.models.functions import Lower
from django.urls import reverse_lazy, reverse
from reservas.library.filters.reservas import *
from reservas.library.forms.reservas import *
from django.db.models import Q, Count
from django.http import JsonResponse
from datetime import datetime
from django.views import View
from django.views.generic import TemplateView
from django.http import Http404

def qs_condiciones(user):
    if user.is_admin:
        return Q()
    elif user.is_moderador:
        return Q(
            Q(usuario=user) | 
            Q(aprobado_por=user) | 
            (Q(espacio__ubicacion=user.ubicacion)  & 
            Q(espacio__piso=user.piso))
        )
    elif user.is_usuario:
        return Q(usuario=user)
    return Q()

class ReservasMonthlyCount(LoginRequiredMixin, PermissionRequiredMixin,View):
    """
    Devuelve un conteo de reservas por día para un rango de fechas,
    opcionalmente filtrado por estado.
    Usado por el calendario para mostrar indicadores de actividad.
    """
    permission_required = 'reservas.view_reserva'
    
    def get(self, request):
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')
        status = request.GET.get('status')

        try:
            if start_str and end_str:
                start_date = datetime.fromisoformat(start_str.split('T')[0])
                end_date = datetime.fromisoformat(end_str.split('T')[0])
            else:
                return JsonResponse({'error': 'Faltan fechas'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Formato de fecha invalido'}, status=400)

        condiciones = qs_condiciones(self.request.user)
        queryset = Reserva.objects.filter(
            condiciones,
            fecha_uso__gte=start_date,
            fecha_uso__lte=end_date,
        )
        

        possible_states = ['pendiente', 'aprobada', 'rechazada']

        if status and status in possible_states:
            queryset = queryset.filter(estado=status)
        else: 
            queryset = queryset.filter(estado__in=possible_states)

        daily_counts = queryset.values('fecha_uso').annotate(
            pendiente_count=Count('id', filter=Q(estado='pendiente')),
            aprobada_count=Count('id', filter=Q(estado='aprobada')),
            rechazada_count=Count('id', filter=Q(estado='rechazada'))
        ).order_by('fecha_uso')
        return JsonResponse(list(daily_counts), safe=False)


class CalendarioReservasView(LoginRequiredMixin, TemplateView):
    """
    Muestra el calendario de reservas
    """
    template_name = 'reservas/calendario.html'


class ReservasByDate(PermissionRequiredMixin, FilterView):
    """
    Muestra una lista de reservas filtradas por fecha
    """
    model = Reserva
    permission_required = 'reservas.view_reserva'
    template_name = 'includes/reservas_cardslist.html'
    paginate_by = 7
    filterset_class = ReservaFilterCards
    context_object_name = 'reservas'   
    ordering = ['hora_inicio']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar parámetros actuales al contexto para la paginación
        context['current_filters'] = self.request.GET.dict()
        
        # Si es una petición HTMX, podemos agregar información adicional
        if self.request.headers.get('HX-Request'):
            context['is_htmx'] = True
            
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        condiciones = qs_condiciones(self.request.user)
        qs = qs.filter(condiciones)
        return qs
 
    
class ReservaListView(LoginRequiredMixin, PermissionRequiredMixin, SmartOrderingMixin, ListCrudMixin, FilterView):
    """
    Muestra una lista de reservas con un formulario de filtrado
    """
    model = Reserva
    permission_required = 'reservas.view_reserva'
    template_name = 'reservas/reservas_table.html'
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
        condiciones = qs_condiciones(self.request.user)
        qs = qs.filter(condiciones)
        return qs
    
class ReservaCreateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, CreateView):
    form_class = ReservaCreateForm
    template_name = 'reservas/reservas_create.html'
    permission_required = 'reservas.add_reserva'
    
    def success_message(self):
        return 'Reserva creada correctamente'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url'] = reverse_lazy('reserva_create')
        ctx['title'] = 'Crear Reserva'
        ctx['subtitle'] = 'Informacion de la reserva'
        return ctx
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        fecha_uso = self.request.GET.get('fecha_uso')
        if fecha_uso:
            initial['fecha_uso'] = fecha_uso
        return initial

class ReservaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, UpdateView ):
    """
    Edita una reserva existente
    """
    model = Reserva
    form_class = ReservaUpdateForm  
    template_name = 'reservas/reservas_edit.html'
    success_url = reverse_lazy('reserva')
    permission_required = 'reservas.change_reserva'

    def success_message(self):
        return 'Reserva editada correctamente'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url'] = reverse_lazy('reserva_edit', args=[self.object.pk])
        ctx['title'] = 'Editar Reserva'
        ctx['subtitle'] = 'Detalles de la reserva'
        return ctx

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        condiciones = qs_condiciones(self.request.user)
        qs = qs.filter(condiciones & Q(estado='pendiente'))
        return qs


class ReservaDetailView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, FormContextMixin, DetailView):
    """
    Muestra los detalles de una reserva
    """
    model = Reserva
    template_name = 'reservas/reservas_detail.html'
    permission_required = 'reservas.view_reserva'
    html_title = 'Detalles de Reserva'
    url = reverse_lazy('reserva_view')

    def get_queryset(self):
        qs = super().get_queryset()
        condiciones = qs_condiciones(self.request.user)
        qs = qs.filter(condiciones)
        return qs

class ReservaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, AjaxDeleteMixin, DeleteView):
    """
    Elimina una reserva existente
    """
    model = Reserva
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('reserva') 
    permission_required = 'reservas.delete_reserva'
    url = 'reserva_delete'

    details = [ 
        {'label': 'Fecha de uso', 'value': 'fecha_uso'},
        {'label': 'Usuario', 'value': 'usuario'},
        {'label': 'Estado', 'value': 'estado'},
        {'label': 'Aprobado por', 'value': 'aprobado_por'},
        {'label': 'Espacio', 'value': 'espacio'},
        {'label': 'Motivo', 'value': 'motivo'},
        {'label': 'Hora inicio', 'value': 'hora_inicio'},
        {'label': 'Hora fin', 'value': 'hora_fin'},
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        condiciones = qs_condiciones(self.request.user)
        qs = qs.filter(condiciones & Q(estado='pendiente'))
        return qs

class ReservaApproveView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, UpdateView):
    """
    Aprobar una reserva existente
    """
    model = Reserva
    form_class = ReservaApproveForm  
    template_name = 'reservas/reservas_approve.html'
    success_url = reverse_lazy('reserva')
    permission_required = 'reservas.change_reserva'

    def success_message(self):
        return 'Reserva editada correctamente'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url'] = reverse_lazy('reserva_approve', args=[self.object.pk])
        ctx['title'] = 'Gestionar Reserva'
        ctx['subtitle'] = 'Aprobar/Rechazar la reserva'
        return ctx

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        if not self.request.user.is_admin and not self.request.user.is_moderador:
            raise Http404
        
        qs = super().get_queryset()
        condiciones = qs_condiciones(self.request.user)
        qs = qs.filter(condiciones & Q(estado='pendiente'))
        return qs

