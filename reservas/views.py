from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin as LoginMixin
from django.shortcuts import redirect
from django.urls import reverse
from reservas.library.utils.utils import get_stats

def custom_404_view(request, exception=None):
    """Custom 404 handler that redirects to login page."""
    return redirect(reverse('login'))

class Dashboard(LoginMixin, TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = get_stats(self.request)
        context['stats'] = stats
        return context
    
    template_name = 'reservas/dashboard.html'