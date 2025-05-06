from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.views import View
from django.template import loader

class HomeView(View):
    def get(self, request):
        template = loader.get_template('index.html')
        return HttpResponse(template.render())
    

class LoginView(View):
    def get(self, request):
        template = loader.get_template('login.html')
        return HttpResponse(template.render())

    def post(self, request):
        return HttpResponse("This is the login view (POST).")


class SignupView(View):
    def get(self, request):
        template = loader.get_template('signup.html')
        return HttpResponse(template.render())

    def post(self, request):
        return HttpResponse("This is the signup view (POST).")