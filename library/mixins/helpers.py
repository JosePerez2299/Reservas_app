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

class AjaxFormMixin:
    def success_message(self):
        return 'Su peticion se ha procesado correctamente'

    def form_invalid(self, form):
        # Retorna el mismo partial con errores (HTTP 200)
        return self.render_to_response(self.get_context_data(form=form))

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
        return ctx


    def export_csv(self):
        """
        Construye el CSV usando exactamente el mismo queryset filtrado + ordenado
        que get_queryset(), pero sin paginación ni template, y con los campos que deseemos.
        """
        # 1) Tomamos todos los objetos (ya filtrados/ordenados y con la anotación):
        qs = self.get_queryset()

        # 2) Definimos qué campos queremos en el CSV. 
        #    Por ejemplo: id, username, email, ubicación, piso, group_name.
        #
        #    Si tuvieras ForeignKey a 'departamento' y quisieras el nombre en vez de ID,
        #    podrías hacer 'departamento__nombre' como vimos antes. Aquí pongo un ejemplo mínimo.
        campos = self.cols.keys()

        # 3) Convertimos a DataFrame. Atención: como 'qs' ya fue anotado con 'group_name',
        #    podemos traerlo directo con .values('group_name'), sin repetir lógica de CASE.
        df = pd.DataFrame(list(qs.values(*campos)))

        # 4) (Opcional) Renombrar columnas para que la cabecera sea más legible:
        df.rename(columns=self.cols, inplace=True)

        # 5) Preparamos la respuesta HTTP tipo CSV
        response = HttpResponse(content_type='text/csv')
        timestamp = now().strftime('%Y%m%d%H%M%S')
        filename = f"{self.model.__name__.lower()}_export_{timestamp}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # 6) Volcamos el DataFrame a CSV directamente sobre la HttpResponse
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
        """
        Obtiene el ordenamiento desde los parámetros GET y aplica la lógica apropiada
        según el tipo de campo del modelo.
        """
        ordering = self.request.GET.get('ordering')
        if not ordering:
            return None
            
        # Remover el signo negativo si existe para obtener el nombre del campo
        field_name = ordering.lstrip('-')
        is_desc = ordering.startswith('-')
        
        # Verificar si es una propiedad mapeada
        if field_name in self.property_to_field_mapping:
            mapped_field = self.property_to_field_mapping[field_name]
            if is_desc:
                return [f'-{mapped_field}']
            else:
                return [mapped_field]
        
        try:
            # Manejar campos relacionados (con __)
            if '__' in field_name:
                return self._handle_related_field_ordering(field_name, is_desc)
            
            # Verificar si el campo existe como atributo del modelo (incluye propiedades)
            if hasattr(self.model, field_name):
                # Verificar si es una propiedad de Python
                if self._is_python_property(field_name):
                    # Las propiedades no se pueden ordenar a nivel de DB
                    # Retornar None para que Django no aplique ordenamiento de DB
                    # y manejar el ordenamiento en Python si es necesario
                    return None
                
                # Si no es una propiedad, intentar obtener el campo del modelo
                try:
                    field = self.model._meta.get_field(field_name)
                    
                    # Verificar si es un campo de texto
                    if self._is_text_field(field):
                        if is_desc:
                            return [Lower(field_name).desc()]
                        else:
                            return [Lower(field_name)]
                    
                    # Para campos numéricos, booleanos u otros tipos
                    else:
                        if is_desc:
                            return [f'-{field_name}']
                        else:
                            return [field_name]
                except:
                    # Si no es un campo de modelo, podría ser una propiedad
                    return None
            else:
                return None
                    
        except Exception:
            # Si hay algún error, usar ordenamiento simple como fallback
            return [ordering]
    
    def _is_python_property(self, field_name):
        """
        Determina si un atributo es una propiedad de Python (@property).
        """
        try:
            attr = getattr(self.model, field_name)
            return isinstance(attr, property)
        except:
            return False

    def _handle_related_field_ordering(self, field_name, is_desc):
        """
        Maneja el ordenamiento para campos relacionados (con __).
        """
        try:
            # Dividir el campo relacionado
            parts = field_name.split('__')
            
            # Navegar por las relaciones para llegar al campo final
            current_model = self.model
            for i, part in enumerate(parts[:-1]):
                try:
                    field = current_model._meta.get_field(part)
                    if hasattr(field, 'related_model'):
                        current_model = field.related_model
                    else:
                        # Si no es una relación, usar ordenamiento simple
                        return [f'-{field_name}'] if is_desc else [field_name]
                except:
                    # Si hay error navegando la relación, usar ordenamiento simple
                    return [f'-{field_name}'] if is_desc else [field_name]
            
            # Obtener el campo final
            final_field_name = parts[-1]
            try:
                final_field = current_model._meta.get_field(final_field_name)
                
                # Si es un campo de texto, usar Lower()
                if self._is_text_field(final_field):
                    if is_desc:
                        return [Lower(field_name).desc()]
                    else:
                        return [Lower(field_name)]
                else:
                    # Para campos numéricos, booleanos, etc.
                    if is_desc:
                        return [f'-{field_name}']
                    else:
                        return [field_name]
                        
            except:
                # Si no se puede acceder al campo final, usar ordenamiento simple
                return [f'-{field_name}'] if is_desc else [field_name]
                
        except Exception:
            # Fallback: ordenamiento simple
            return [f'-{field_name}'] if is_desc else [field_name]

    def _is_text_field(self, field):
        """
        Determina si un campo es de tipo texto y requiere Lower() para ordenamiento.
        """
        # Tipos de campo que son considerados texto
        text_field_types = (
            models.CharField,
            models.TextField,
            models.SlugField,
            models.EmailField,
            models.URLField,
        )
        
        # Verificar por tipo de campo
        if isinstance(field, text_field_types):
            return True
            
        # Verificar por nombre de clase (útil para campos personalizados)
        field_class_name = field.__class__.__name__
        text_field_class_names = [
            'CharField', 'TextField', 'SlugField', 
            'EmailField', 'URLField', 'JSONField'
        ]
        
        return field_class_name in text_field_class_names