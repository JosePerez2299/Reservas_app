from django.http import HttpResponse
from django.urls import path
from reservas.views import *  
urlpatterns = [
    path('', HomeView.as_view()), 
    path('login', Login.as_view()),
    path('signup', SignupView.as_view()),
    path('user', UserDashboardView.as_view(), name='user_dashboard'),
    path('manager', ManagerDashboardView.as_view(), name ='manager_dashboard'),
    ]