"""
Views para las reservas

* ReservaListView: Muestra una lista de reservas con un formulario de filtrado
* ReservaCreateView: Crea una nueva reserva
* ReservaUpdateView: Edita una reserva existente
* ReservaDetailView: Muestra los detalles de una reserva
* ReservaDeleteView: Elimina una reserva existente

"""

from django.shortcuts import render

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from reservas.models import Reserva
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters.views import FilterView
from reservas.library.mixins.helpers import *
from django.db.models.functions import Lower
from django.urls import reverse_lazy, reverse
from reservas.library.filters.reservas import *
from reservas.library.forms.reservas import ReservaCreateForm, ReservaUpdateForm
from django.db.models import Q, Count
from django.http import JsonResponse
from datetime import datetime
from django.views import View
from django.views.generic import TemplateView

class Reservas_json(LoginRequiredMixin, PermissionRequiredMixin,View):
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

        queryset = Reserva.objects.filter(
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


def reservas_by_date_json(request):
    """
    Devuelve una lista detallada de reservas para una fecha específica.
    """
    date_str = request.GET.get('fecha')
    status = request.GET.get('status')

    try:
        target_date = datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError, AttributeError):
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    reservas = Reserva.objects.filter(fecha_uso=target_date)

    if status and status != 'all':
        reservas = reservas.filter(estado=status)
    
    reservas_values = reservas.values(
        'id', 'usuario_id', 'espacio_id', 'fecha_uso', 'hora_inicio',
        'hora_fin', 'estado', 'motivo', 'motivo_admin', 'aprobado_por_id',
        'usuario__first_name', 'usuario__last_name', 'usuario__username',
        'espacio__nombre'
    ).order_by('hora_inicio')



    data = []
    for r in reservas_values:
        full_name = f"{r['usuario__first_name']} {r['usuario__last_name']}".strip()
        data.append({
            'id': r['id'],
            'usuario_id': r['usuario_id'],
            'usuario_nombre': full_name or r['usuario__username'],
            'espacio_id': r['espacio_id'],
            'espacio_nombre': r['espacio__nombre'],
            'fecha_uso': r['fecha_uso'].strftime('%Y-%m-%d'),
            'hora_inicio': r['hora_inicio'].strftime('%H:%M'),
            'hora_fin': r['hora_fin'].strftime('%H:%M'),
            'estado': r['estado'],
            'motivo': r['motivo'],
            'motivo_admin': r['motivo_admin'] or '',
            'aprobado_por': r['aprobado_por_id'],
            'edit_url': reverse('reserva_edit', args=[r['id']]),
        })

    print(data)

    return JsonResponse(data, safe=False)


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
    
    

   
class ReservaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Crea una nueva reserva
    """
    model = Reserva
    form_class = ReservaCreateForm
    template_name = 'reservas/reservas_create.html'
    success_url = reverse_lazy('reserva')
    permission_required = 'reservas.add_reserva'
    html_title = 'Crear Reserva'

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        # 1) aseguramos asignar usuario y guardar
        form.instance.usuario = self.request.user
        self.object = form.save()

        # 2) si viene por HTMX, devolvemos 200 con trigger
        if self.request.headers.get('HX-Request') == 'true':
            resp = HttpResponse(status=200)
            resp['HX-Trigger'] = 'showSuccess'
            return resp

        # 3) si no, comportamiento normal (redirect)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Si es petición HTMX, devolvemos el form con errores y status 400
        
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context, status=200)


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