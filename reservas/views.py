from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin as LoginMixin

class Dashboard(LoginMixin, TemplateView):
    template_name = 'reservas/dashboard.html'