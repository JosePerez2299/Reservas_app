from django.http import HttpResponse
from django.urls import path
from reservas.views import *  
urlpatterns = [
    path('', HomeView.as_view()), 
    path('login', LoginView.as_view()),
    path('signup', SignupView.as_view()),
    ]