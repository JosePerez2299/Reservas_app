from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.models import Group
from django.views.generic import TemplateView, CreateView
from django.template import loader
from reservas.utils.forms.auth import UserCreationForm

class Signup(CreateView):
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