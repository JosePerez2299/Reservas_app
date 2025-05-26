from django.http import JsonResponse

class AjaxFormMixin:
    def form_invalid(self, form):
        html = self.render_to_response(self.get_context_data(form=form)).rendered_content
        return JsonResponse({'success': False, 'html_form': html})

    def form_valid(self, form):
        # Guarda y asigna a self.object
        self.object = form.save()
        return JsonResponse({
            'success': True,
            'redirect_url': self.get_success_url()
        })