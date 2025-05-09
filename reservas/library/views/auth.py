from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views import View
from django.contrib.auth.models import Group
from django.views.generic import TemplateView, CreateView
from django.template import loader
from reservas.library.forms.auth import UserCreationForm

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'auth/signup.html'
    success_url = reverse_lazy('')  

    def form_valid(self, form):
        response = super().form_valid(form)
        return response