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
from django.db import IntegrityError, transaction
from django.core.files.storage import FileSystemStorage
from formtools.wizard.views import SessionWizardView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import json


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


class EspacioUpdateWizardView(LoginRequiredMixin, PermissionRequiredMixin, SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'tmp'))
    permission_required = 'espacios.change_espacio'   # <-- permiso de cambio
    form_list = [
        ('espacio', EspacioForm),
        ('detalle_digital', DetalleDigitalForm),
        ('detalle_fisico', DetalleFisicoForm),
        ('resumen', EmptyForm),
    ]
    condition_dict = {
        'detalle_digital': es_espacio_digital,
        'detalle_fisico': es_espacio_fisico
    }

    def dispatch(self, request, *args, **kwargs):
        # Carga la instancia que vamos a editar (pk en la URL)
        self.espacio = get_object_or_404(Espacio, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edición de Espacio'
        ctx['subtitle'] = 'Modifica la información necesaria'
        ctx['header_icon'] = 'building'
        ctx['url'] = reverse_lazy('espacio_edit', kwargs={'pk': self.espacio.pk})

        all_steps = list(self.get_form_list().keys())
        current_index = all_steps.index(self.steps.current)
        ctx['all_steps'] = all_steps
        ctx['current_index'] = current_index
        ctx['is_update'] = True
        if self.steps.current == 'resumen':
            ctx['resumen_data'] = self.get_resumen_data()

        return ctx

    def get_resumen_data(self):
        espacio_data = self.get_cleaned_data_for_step('espacio') or {}
        detalle_data = {}

        tipo = espacio_data.get('tipo') or getattr(self.espacio, 'tipo', None)
        if tipo == Espacio.Tipo.DIGITAL:
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

    # Si tus formularios son ModelForm -> devuelve la instancia correspondiente
    def get_form_instance(self, step):
        if step == 'espacio':
            return self.espacio
        if step == 'detalle_digital':
            # asumo relación one-to-one o FK con related_name 'detalle_digital'
            try:
                return self.espacio.detalle_digital
            except (AttributeError, DetalleDigital.DoesNotExist):
                return None
        if step == 'detalle_fisico':
            try:
                return self.espacio.detalle_fisico
            except (AttributeError, DetalleFisico.DoesNotExist):
                return None
        return None


    def done(self, form_list, **kwargs):
        # form_list ya está binded; si son ModelForm con instancia, save() actualizará
        espacio_form = form_list[0]  # ModelForm con instancia -> save() actualiza
        detalle_digital_form = None
        detalle_fisico_form = None

        # dependiendo del tipo el wizard habrá incluido uno u otro
        for form in form_list[1:]:
            # distingues por form.__class__ o por step names si prefieres
            if isinstance(form, DetalleDigitalForm):
                detalle_digital_form = form
            elif isinstance(form, DetalleFisicoForm):
                detalle_fisico_form = form

        try:
            # Guardar/actualizar Espacio
            espacio = espacio_form.save()  # actualiza porque get_form_instance devolvió la instancia

            # Guardar detalle digital (si existe en este flujo)
            if detalle_digital_form:
                detalle = detalle_digital_form.save(commit=False)
                detalle.espacio = espacio  # asegurar relación
                detalle.save()

            # Guardar detalle físico (si existe)
            if detalle_fisico_form:
                detalle = detalle_fisico_form.save(commit=False)
                detalle.espacio = espacio
                detalle.save()

            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({'showMessage': 'Se ha actualizado exitosamente'})
            # opcional: limpiar datos de wizard en session
            self.storage.reset()
            return response

        except Exception as e:
            # loguea e si quieres
            response = HttpResponse(status=500)
            response['HX-Trigger'] = json.dumps({'showMessage': 'Error al actualizar el espacio'})
            return response

class EspacioDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Espacio
    permission_required = 'espacios.view_espacio'
    template_name = "reservas/espacio_detail.html"
    context_object_name = "espacio"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Detalles del Espacio'
        ctx['subtitle'] = 'Información del espacio'
        if self.object.tipo == Espacio.Tipo.DIGITAL:
            ctx['header_icon'] = 'laptop'
        elif self.object.tipo == Espacio.Tipo.FISICO:
            ctx['header_icon'] = 'building'
        return ctx

class EspacioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, AjaxDeleteMixin, DeleteView):
    """
    Elimina un espacio existente
    """
    model = Espacio
    permission_required = 'espacios.delete_espacio'
    template_name = 'reservas/delete.html'
    success_url = reverse_lazy('espacios    ') 
    url = 'espacio_delete'
    details = [ 
        {'label': 'Nombre', 'value': 'nombre'},
        {'label': 'Tipo', 'value': 'tipo'},
        {'label': 'Capacidad', 'value': 'capacidad_maxima'},
        {'label': 'Ubicación', 'value': 'ubicacion'},
        {'label': 'Disponible', 'value': 'disponible'},
    ]