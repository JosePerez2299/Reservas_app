from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
import pandas as pd
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import now
from django.urls import reverse_lazy

class AjaxFormMixin:
    def post(self, request, *args, **kwargs):
        # Llamamos al dispatch normal para procesar form_valid/form_invalid
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return super().post(request, *args, **kwargs)
        # No es AJAX: comportamiento normal
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        # Solo AJAX: devolvemos HTML del form con errores
        html = render_to_string(
            self.template_name, 
            self.get_context_data(form=form), 
            request=self.request
        )
        return JsonResponse({'success': False, 'html': html})

    def form_valid(self, form):
        # Guardamos instancia
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.get_success_url()
            })
        # No AJAX: redirección normal

class FormContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = self.html_title + ' - ' + str    (self.object.pk) if self.object else self.html_title
        
        if self.object is not None:
            ctx['url'] = reverse_lazy(self.url, args=[self.object.pk])
        else:
            ctx['url'] = reverse_lazy(self.url)
        return ctx


class ListContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['model'] = self.model.__name__.lower()
        ctx['create_url'] = self.crud_urls['create']
        ctx['view_url'] = self.crud_urls['view']
        ctx['edit_url'] = self.crud_urls['edit']
        ctx['delete_url'] = self.crud_urls['delete']      

        # Definir las columnas que se mostrarán en la tabla
        ctx['cols'] = self.cols
        return ctx


class ExportMixin:

    def get(self, request, *args, **kwargs):
        """
        Si existe ?export=csv en la URL, devolvemos CSV. Si no, delegamos
        a la implementación normal de FilterView (HTML + paginación).
        """
        if request.GET.get('export') == 'csv':
            return self.export_csv()
        return super().get(request, *args, **kwargs)



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
        filename = f"reservas_export_{timestamp}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # 6) Volcamos el DataFrame a CSV directamente sobre la HttpResponse
        df.to_csv(response, index=False)

        return response