"""
Views para los espacios

* EspacioListView: Muestra una lista de espacios con un formulario de filtrado
* EspacioCreateView: Crea un nuevo espacio
* EspacioUpdateView: Edita un espacio existente
* EspacioDetailView: Muestra los detalles de un espacio
* EspacioDeleteView: Elimina un espacio existente

"""

from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views import View
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
    

class EspacioCreateView( View):
    template_name = "reservas/espacios_create.html"

    def get(self, request, *args, **kwargs):
        contexto = {
            'espacio_form': EspacioForm(prefix='esp'),
            'detalle_digital_form': DetalleDigitalForm(prefix='dig'),
            'detalle_fisico_form': DetalleFisicoForm(prefix='fis'),
        }
        return render(request, self.template_name, contexto)

    def post(self, request, *args, **kwargs):
        espacio_form = EspacioForm(request.POST, prefix='esp')
        tipo = request.POST.get('esp-tipo')  # name incluye el prefijo
        detalle_form = (DetalleDigitalForm(request.POST, prefix='dig')
                        if tipo == 'digital'
                        else DetalleFisicoForm(request.POST, prefix='fis'))

        print('entra')
        print(detalle_form.errors)
        print(espacio_form.is_valid())
        print(detalle_form.is_valid())

        if espacio_form.is_valid() and detalle_form.is_valid():
            try:
                with transaction.atomic():
                    espacio = espacio_form.save()
                    detalle = detalle_form.save(commit=False)
                    detalle.espacio_id = espacio.id
                    detalle.save()

                print("se guardo el espacio")
                response = HttpResponse(status=204)
                response['HX-Trigger'] = json.dumps({'showMessage': 'Espacio creado correctamente'})
                return response
            except IntegrityError as e:
                espacio_form.add_error(None, "Error de integridad al guardar.")
        # si hay errores, re-renderiza mostrando ambos formularios con datos y errores
        contexto = {
            'espacio_form': espacio_form,
            'detalle_digital_form': DetalleDigitalForm(prefix='dig') if tipo!='digital' else detalle_form,
            'detalle_fisico_form': DetalleFisicoForm(prefix='fis') if tipo!='fisico' else detalle_form,
        }
        return render(request, self.template_name, contexto)

# views.py - Usando FormTools
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from formtools.wizard.views import SessionWizardView, NamedUrlSessionWizardView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json



def es_espacio_digital(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('espacio') or {}
    return cleaned_data.get('tipo') == Espacio.Tipo.DIGITAL

def es_espacio_fisico(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('espacio') or {}
    return cleaned_data.get('tipo') ==  Espacio.Tipo.FISICO


class EspacioWizardView(SessionWizardView):
    template_name = "reservas/espacios_create.html"
    form_list = [('espacio', EspacioForm), ('detalle_digital', DetalleDigitalForm), ('detalle_fisico', DetalleFisicoForm)]
    # condition_dict = {'1': es_espacio_digital, '2': es_espacio_fisico}

    condition_dict = {'detalle_digital': es_espacio_digital, 'detalle_fisico': es_espacio_fisico}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # contador fijo
        ctx['display_steps_count'] = 2
        # si estamos en el primer step del wizard original -> mostrar 1,
        # si estamos en alguno de los detalles (1 o 2) -> mostrar 2
        ctx['display_step_number'] = 1 if self.steps.current == 'espacio' else 2
        return ctx

    def done(self, form_list, **kwargs):
        espacio_form = form_list[0]
        detalle_form = form_list[1]

        print('form_list', form_list)
        with transaction.atomic():
                espacio = espacio_form.save()
                detalle = detalle_form.save(commit=False)
                detalle.espacio_id = espacio.id
                detalle.save()

        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({'showMessage': 'Se ha creado exitosamente'})
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