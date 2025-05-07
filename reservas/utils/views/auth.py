from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.models import Group
from django.views.generic import TemplateView, CreateView
from django.template import loader
from reservas.forms import UserCreationForm

class LoginView(View):
    def get(self, request):
        template = loader.get_template('auth/login.html')
        return HttpResponse(template.render())

    def post(self, request):
        return HttpResponse("This is the login view (POST).")


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'auth/signup.html'
    success_url = reverse_lazy('')  # Cambia esto a donde quieras redirigir al usuario

    def form_valid(self, form):
        response = super().form_valid(form)
        # Iniciar sesión automáticamente
        login(self.request, self.object)
        # Añadir al grupo 'usuario'
        # grupo = Group.objects.get(name='usuario')
        # self.object.groups.add(grupo)
        return response