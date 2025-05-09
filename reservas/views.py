from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from reservas.utils.utils import get_access
from reservas.library.views.auth import SignupView
from django.contrib.auth.mixins import LoginRequiredMixin as LoginMixin

class Login(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True  

class Signup(LoginMixin, SignupView):
    redirect_authenticated_user = True  

class Dashboard(LoginMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user 
        models = get_access(user)
        print(models)
        return render(request, 'dashboard.html', {'models': models})
    