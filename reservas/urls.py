from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import path, reverse
from django.contrib.auth.views import LogoutView, LoginView
from reservas.library.views.usuarios import *
from reservas.views import *
from reservas.library.views.espacios import *
from reservas.library.views.reservas import *
from reservas.library.views.logs import *

urlpatterns = [
    path('', LoginView.as_view(template_name='reservas/login.html', redirect_authenticated_user=True), name='login'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('log/', LogListView.as_view(), name='log'),
    path('log/<int:pk>/', LogDetailView.as_view(), name='log_detail'),

    path('espacio/', EspacioListView.as_view(), name='espacio'),
    path('espacio/create/', EspacioCreateView.as_view(), name='espacio_create'),
    path('espacio/view/<int:pk>/', EspacioDetailView.as_view(), name='espacio_view'),
    path('espacio/edit/<int:pk>/', EspacioUpdateView.as_view(), name='espacio_edit'),
    path('espacio/delete/<int:pk>/', EspacioDeleteView.as_view(), name='espacio_delete'),


    path('usuario/', UsuarioListView.as_view(), name='usuario'),
    path('usuario/create/', UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuario/view/<int:pk>/', UsuarioDetailView.as_view(), name='usuario_view'),
    path('usuario/edit/<int:pk>/', UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('usuario/delete/<int:pk>/', UsuarioDeleteView.as_view(), name='usuario_delete'),

    path('reserva/', ReservaListView.as_view(), name='reserva'),
    path('reserva/create/', ReservaCreateView.as_view(), name='reserva_create'),
    path('reserva/view/<int:pk>/', ReservaDetailView.as_view(), name='reserva_view'),
    path('reserva/edit/<int:pk>/', ReservaUpdateView.as_view(), name='reserva_edit'),
    path('reserva/delete/<int:pk>/', ReservaDeleteView.as_view(), name='reserva_delete'),
    path('calendario/', CalendarioReservasView.as_view(), name='calendario'),
    path('api/reservas/', Reservas_json.as_view(), name='reservas_json'),
    path('api/reservas/daily/', reservas_by_date_json, name='reservas_by_date_json'),

    path('reservas/fecha/', ReservasByDate.as_view(), name='reservas_cards'),
]

# Manejador de error 404
