from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string

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
