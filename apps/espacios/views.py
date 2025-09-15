"""
Views para los espacios

* EspacioListView: Muestra una lista de espacios con un formulario de filtrado
* EspacioCreateView: Crea un nuevo espacio
* EspacioUpdateView: Edita un espacio existente
* EspacioDetailView: Muestra los detalles de un espacio
* EspacioDeleteView: Elimina un espacio existente

"""

import os
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views import View
from apps.espacios.services import *
from .forms import *
from .filters import EspacioFilter
from .models import Espacio
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters.views import FilterView
from library.mixins.helpers import *
from django.urls import reverse_lazy
from django.db.models.functions import Lower
from django.db.models import Count, Q   
from django.db import IntegrityError, transaction
from django.core.files.storage import FileSystemStorage
from formtools.wizard.views import SessionWizardView

class EspacioListView(LoginRequiredMixin, ListCrudMixin, SmartOrderingMixin, PermissionRequiredMixin, FilterView):
    """
    Muestra una lista de espacios con un formulario de filtrado
    """
    model = Espacio
    permission_required = 'espacios.view_espacio'
    template_name = 'reservas/espacio_table.html'
    paginate_by = 10
    filterset_class = EspacioFilter
    can_export = True

    cols = {
        'id': 'ID',
        'nombre': 'Nombre',
        'tipo': 'Tipo',
        'capacidad_maxima': 'Capacidad',
        'ubicacion': 'Ubicación',
        'disponible': 'Disponible',
    }

    crud_urls = {
        'create': 'espacio_create',
        'view': 'espacio_view',
        'edit': 'espacio_edit', 
        'delete': 'espacio_delete',
    }
    
def es_espacio_digital(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('espacio') or {}
    return cleaned_data.get('tipo') == Espacio.Tipo.DIGITAL

def es_espacio_fisico(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('espacio') or {}
    return cleaned_data.get('tipo') == Espacio.Tipo.FISICO



class EspacioCreateWizardView(LoginRequiredMixin, PermissionRequiredMixin, SessionWizardView):
    file_storage = FileSystemStorage(  location=os.path.join(settings.MEDIA_ROOT, 'tmp'))
    permission_required = 'espacios.add_espacio'
    form_list = [
        ('espacio', EspacioForm), 
        ('detalle_digital', DetalleDigitalForm), 
        ('detalle_fisico', DetalleFisicoForm),
        ('resumen', EmptyForm)  
    ]
    
    condition_dict = {
        'detalle_digital': es_espacio_digital, 
        'detalle_fisico': es_espacio_fisico
    }
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Creación de Espacio'
        ctx['subtitle'] = 'Complete la información requerida'
        ctx['header_icon'] = 'building'
        ctx['url'] = reverse_lazy('espacio_create')
        
        # Steps info
        all_steps = list(self.get_form_list().keys())
        current_index = all_steps.index(self.steps.current)
        
        ctx['all_steps'] = all_steps
        ctx['current_index'] = current_index
        
        if self.steps.current == 'resumen':

            ctx['resumen_data'] = self.get_resumen_data()
            
        return ctx
    
    def get_resumen_data(self):
        """Recopila todos los datos del wizard para mostrar en el resumen"""
        espacio_data = self.get_cleaned_data_for_step('espacio') or {}
        detalle_data = {}
        
        if espacio_data.get('tipo') == Espacio.Tipo.DIGITAL:
            detalle_data = self.get_cleaned_data_for_step('detalle_digital') or {}
            tipo_detalle = 'Digital'
        else:
            detalle_data = self.get_cleaned_data_for_step('detalle_fisico') or {}
            tipo_detalle = 'Físico'
        
        return {
            'espacio': espacio_data,
            'detalle': detalle_data,
            'tipo_detalle': tipo_detalle
        }

    def get_template_names(self):
        TEMPLATES = {
            "espacio": "espacios/espacio_form.html",
            "detalle_digital": "espacios/detalles_digitales_form.html",
            "detalle_fisico": "espacios/detalles_fisicos_form.html",
            "resumen": "espacios/confirm_create.html" 
        }
        return [TEMPLATES[self.steps.current]]
        
    def done(self, form_list, **kwargs):
        espacio_form = form_list[0]
        detalle_form = form_list[1]
        espacio_creado = create_espacio(espacio_form, detalle_form)
        if espacio_creado:
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({'showMessage': 'Se ha creado exitosamente'})
            return response
        else:
            response = HttpResponse(status=500)
            response['HX-Trigger'] = json.dumps({'showMessage': 'Error al crear el espacio'})
            return response


class EspacioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, AjaxFormMixin, UpdateView):
    """
    Edita un espacio existente
    """
    model = Espacio
    permission_required = 'espacios.change_espacio'
    form_class = EspacioUpdateForm
    template_name = 'reservas/espacios_edit.html'
    success_url = reverse_lazy('espacio')
    html_title = 'Editar Espacio'

    def get_form_kwargs(self):
        """
        Pasa el objeto request al formulario
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs   

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Editar Espacio'
        ctx['url'] = reverse_lazy('espacio_edit', args=[self.object.pk])
        ctx['subtitle'] = 'Información del espacio'
        return ctx




class EspacioDetailView(LoginRequiredMixin, PermissionRequiredMixin, FormContextMixin, DetailView):
    model = Espacio
    template_name = 'reservas/espacio_detail.html'
    permission_required = 'espacios.view_espacio'
    context_object_name = 'object'
    html_title = 'Detalles del Espacio'
    url = 'espacio_view'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        espacio = self.get_object()
        
        # Obtener estadísticas de reservas
        reservas_stats = Reserva.objects.filter(espacio=espacio).aggregate(
            total=Count('id'),
            aprobadas=Count('id', filter=Q(estado='aprobada')),
            pendientes=Count('id', filter=Q(estado='pendiente')),
            rechazadas=Count('id', filter=Q(estado='rechazada'))
        )
        
        context['total_reservas'] = reservas_stats['total']
        context['reservas_aprobadas'] = reservas_stats['aprobadas']
        context['reservas_pendientes'] = reservas_stats['pendientes']
        context['reservas_rechazadas'] = reservas_stats['rechazadas']
        
        return context

class EspacioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, AjaxDeleteMixin, DeleteView):
    """
    Elimina un espacio existente
    """
    model = Espacio
    permission_required = 'espacios.delete_espacio'
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('espacio') 
    url = 'espacio_delete'
    details = [ 
        {'label': 'Nombre', 'value': 'nombre'},
        {'label': 'Tipo', 'value': 'tipo'},
        {'label': 'Capacidad', 'value': 'capacidad_maxima'},
        {'label': 'Ubicación', 'value': 'ubicacion'},
        {'label': 'Disponible', 'value': 'disponible'},
    ]