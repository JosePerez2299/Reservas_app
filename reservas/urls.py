from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from reservas.library.views.usuarios import *
from reservas.views import *
from reservas.library.views.espacios import *
from reservas.library.views.reservas import *
urlpatterns = [
    path('', LoginView.as_view(template_name='reservas/login.html', redirect_authenticated_user=True), name='login'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # TODO Logout
    # Espacio crud
    path('espacio/', EspacioListView.as_view(), name='espacio'),
    path('espacio/create/', EspacioCreateView.as_view(), name='espacio_create'),
    path('espacio/view/<int:pk>/', EspacioDetailView.as_view(), name='espacio_view'),
    path('espacio/edit/<int:pk>/', EspacioUpdateView.as_view(), name='espacio_edit'),
    path('espacio/delete/<int:pk>/', EspacioDeleteView.as_view(), name='espacio_delete'),

    path('usuario/', EspacioListView.as_view(), name='usuario'),
    path('usuario/create/', EspacioCreateView.as_view(), name='usuario_create'),
    path('usuario/view/<int:pk>/', EspacioListView.as_view(), name='usuario_list'),
    path('usuario/edit/<int:pk>/', EspacioListView.as_view(), name='usuario_edit'),
    path('usuario/delete/<int:pk>/', EspacioListView.as_view(), name='usuario_delete'),

    path('reserva/', ReservaListView.as_view(), name='reserva'),
    path('reserva/create/', ReservaCreateView.as_view(), name='reserva_create'),
    path('reserva/view/<int:pk>/', ReservaDetailView.as_view(), name='reserva_view'),
    path('reserva/edit/<int:pk>/', ReservaUpdateView.as_view(), name='reserva_edit'),
    path('reserva/delete/<int:pk>/', ReservaDeleteView.as_view(), name='reserva_delete'),
]
