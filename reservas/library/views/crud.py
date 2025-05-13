from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, CreateView
from my_app.settings import DASHBOARD_ACCESS
from django.contrib.auth.mixins import LoginRequiredMixin as LoginMixin
from reservas.library.utils.utils import get_user_groups

class CrudView(LoginMixin, View):
    def get(self, request, current_section):
        context = {
            'current_section' : current_section
        }

        groups = get_user_groups(request.user)
        for group in groups:
            # Validar en el contexto global, no los permisos de BD
            if current_section in DASHBOARD_ACCESS[group]:
              return render(request, 'crud.html', context)
        return redirect('dashboard')
