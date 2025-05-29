from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin as LoginMixin
from django.shortcuts import redirect
from django.urls import reverse

def custom_404_view(request, exception=None):
    """Custom 404 handler that redirects to login page."""
    return redirect(reverse('login'))

class Dashboard(LoginMixin, TemplateView):
    template_name = 'reservas/dashboard.html'