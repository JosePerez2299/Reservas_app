from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import path, reverse
from django.contrib.auth.views import LogoutView, LoginView
from apps.usuarios.views import ProfileView
from reservas.library.views.usuarios import *
from reservas.views import *
from reservas.library.views.espacios import *
from reservas.library.views.reservas import *
from reservas.library.views.logs import *


urlpatterns = [
    path('', LoginView.as_view(template_name='reservas/login.html', redirect_authenticated_user=True), name='login'),
    path('inicio/', Dashboard.as_view(), name='dashboard'),
    path('perfil/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('log/', LogListView.as_view(), name='log'),
    path('log/<int:pk>/', LogDetailView.as_view(), name='log_detail'),


    path('reservas/', ReservaListView.as_view(), name='reserva'),
    path('reservas/create/', ReservaCreateView.as_view(), name='reserva_create'),
    path('reservas/view/<int:pk>/', ReservaDetailView.as_view(), name='reserva_view'),
    path('reservas/edit/<int:pk>/', ReservaUpdateView.as_view(), name='reserva_edit'),
    path('reservas/delete/<int:pk>/', ReservaDeleteView.as_view(), name='reserva_delete'),
    path('calendario/', CalendarioReservasView.as_view(), name='calendario'),
    path('api/reservas/', ReservasMonthlyCount.as_view(), name='reservas_monthly_count'),

    path('api/reservas/fecha/', ReservasByDate.as_view(), name='reservas_by_date'),
    path('reserva/gestionar/<int:pk>/', ReservaApproveView.as_view(), name='reserva_approve'),
]

# Manejador de error 404
