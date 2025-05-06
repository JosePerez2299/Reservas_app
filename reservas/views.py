from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.views import View
from django.template import loader
from reservas.forms import SignUpForm

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
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')   # o la URL que quieras
        return render(request, 'signup.html', {'form': form})
