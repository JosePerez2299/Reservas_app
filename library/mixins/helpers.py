from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
import pandas as pd
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import now
from django.urls import reverse_lazy
from django.db.models.functions import Lower
from django.db import models
from django.conf import settings
import json
from django.db.models.fields.related import ManyToManyField
from django.db.models import F


class AjaxFormMixin:
    def success_message(self):
        return 'Su peticion se ha procesado correctamente'

    def form_invalid(self, form):
        # Retorna el mismo partial con errores (HTTP 200)
        response = self.render_to_response(self.get_context_data(form=form))
        # Agregar trigger para hacer scroll a los errores
        response['HX-Trigger'] = json.dumps({'scrollToErrors': True})
        return response

    def form_valid(self, form):
        form.save()
        
        response = HttpResponse(status=204)
        # disparamos showMessage con payload sencillo
        response['HX-Trigger'] = json.dumps({'showMessage': self.success_message()})
        return response
        
class AjaxDeleteMixin:
    """
    Mixin para añadir un HX-Trigger a las respuestas de DeleteView.
    """
    success_message = "Eliminación exitosa"

    def form_valid(self, form):
        # 1) Obtén el objeto antes de borrarlo (por si necesitas datos)
        obj = self.get_object()

        # 2) Aquí puedes disparar tu evento "antes" si lo necesitas,
        #    p.ej. logger, signals, etc.
        #    do_something_before_delete(obj)

        # 3) Borra el objeto
        response = super().delete(form)

        response = HttpResponse(status=204)
        response["HX-Trigger"] = json.dumps({
            "showMessage": self.success_message
        })
        return response


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model'] = self.model.__name__
        
        ctx['url'] = reverse_lazy(self.url, args=[self.object.pk])
        ctx['details'] = [{'label': detail['label'], 'value': str(getattr(self.object, detail['value']) )} for detail in self.details]
        return ctx

class FormContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = self.html_title + ' - ' + str    (self.object.pk) if self.object else self.html_title
        
        if self.object is not None:
            ctx['url'] = reverse_lazy(self.url, args=[self.object.pk])
        else:
            ctx['url'] = reverse_lazy(self.url)
        return ctx


class ListCrudMixin:
    
    def get(self, request, *args, **kwargs):
        """
        Si existe ?export=csv en la URL, devolvemos CSV. Si no, delegamos
        a la implementación normal de FilterView (HTML + paginación).
        """
        try:
            if self.can_export and request.GET.get('export') == 'csv':
                return self.export_csv()
        except AttributeError:
            return super().get(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        
        ctx = super().get_context_data(**kwargs)
        ctx['model'] = settings.MODELOS.dict[self.model.__name__]

        try:
            ctx['crud_urls'] = self.crud_urls
            ctx['can_export'] = self.can_export 
        except AttributeError:
            pass

        # Definir las columnas que se mostrarán en la tabla
        try:
            ctx['cols'] = self.cols
        except AttributeError:
            ctx['cols'] = {field.name: field.verbose_name for field in self.model._meta.get_fields()}
        
        try:
            ctx['actions'] = self.actions
        except AttributeError:
            ctx['actions'] = True

        try:
            ctx['sortable_fields'] = self.sortable_fields
        except AttributeError:
            ctx['sortable_fields'] = []
        return ctx




    def export_csv(self):
        qs = self.get_queryset()
        campos = self.cols.keys()

        data = []
        for obj in qs:
            row = {}
            for col in campos:
                value = None

                if "__" in col:
                    # soporte para lookups tipo "fk__campo"
                    value = obj
                    for part in col.split("__"):
                        value = getattr(value, part, "")
                        if value is None:
                            break
                else:
                    try:
                        field = obj._meta.get_field(col)
                    except Exception:
                        field = None

                    attr = getattr(obj, col, None)

                    # Caso: ManyToMany
                    if isinstance(field, ManyToManyField):
                        value = ", ".join(str(v) for v in attr.all())

                    # Caso: método o propiedad
                    elif callable(attr):
                        value = attr()

                    # Caso normal
                    else:
                        value = attr

                row[col] = value
            data.append(row)

        df = pd.DataFrame(data)
        df.rename(columns=self.cols, inplace=True)

        response = HttpResponse(content_type="text/csv")
        timestamp = now().strftime("%Y%m%d%H%M%S")
        filename = f"{self.model.__name__.lower()}_export_{timestamp}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        df.to_csv(response, index=False)
        return response





class SmartOrderingMixin:
    """
    Mixin que proporciona ordenamiento inteligente basado en el tipo de campo.
    Aplica Lower() solo a campos de texto y ordenamiento directo a campos numéricos/booleanos.
    También maneja propiedades de Python que no son campos de base de datos.
    """
    
    # Mapeo de propiedades de Python a campos de base de datos para ordenamiento
    property_to_field_mapping = {}
    
    def get_ordering(self):
            ordering = self.request.GET.get('ordering')
            if not ordering:
                return None

            field_name = ordering.lstrip('-')
            is_desc = ordering.startswith('-')

            if field_name in self.property_to_field_mapping:
                mapped_field = self.property_to_field_mapping[field_name]
                return [f'-{mapped_field}' if is_desc else mapped_field]

            try:
                if '__' in field_name:
                    return self._handle_related_field_ordering(field_name, is_desc)

                if hasattr(self.model, field_name):
                    if self._is_python_property(field_name):
                        return None

                    field = self.model._meta.get_field(field_name)
                    if self._is_text_field(field):
                        return [Lower(F(field_name)).desc()] if is_desc else [Lower(F(field_name)).asc()]
                    else:
                        return [f'-{field_name}' if is_desc else field_name]
                return None
            except Exception:
                return [ordering]
