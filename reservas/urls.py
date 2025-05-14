from django.http import HttpResponse
from django.urls import path
from reservas.library.views.usuarios import *
from reservas.views import *
from reservas.library.views.espacios import *
urlpatterns = [
    path('', Login.as_view(), name='home'),
    path('login/', Login.as_view(), name='login'),
    path('signup/', Signup.as_view(), name='signup'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    # TODO Logout
    path('dashboard/', Dashboard.as_view(), name='logout'),
    # Espacio crud
    path('espacio/', EspacioListView.as_view(), name='espacio'),
    path('espacio/create/', EspacioCreateView.as_view(), name='espacio_create'),
    path('espacio/view/<int:pk>/', EspacioListView.as_view(), name='espacio_view'),
    path('espacio/edit/<int:pk>/', EspacioUpdateView.as_view(), name='espacio_edit'),
    path('espacio/delete/<int:pk>/', EspacioDeleteView.as_view(), name='espacio_delete'),

    path('usuario/', EspacioListView.as_view(), name='usuario'),
    path('usuario/create/', EspacioCreateView.as_view(), name='usuario_create'),
    path('usuario/view/<int:pk>/', EspacioListView.as_view(), name='usuario_list'),
    path('usuario/edit/<int:pk>/', EspacioUpdateView.as_view(), name='usuario_edit'),
    path('usuario/delete/<int:pk>/', EspacioDeleteView.as_view(), name='usuario_delete'),

    path('reserva/', EspacioListView.as_view(), name='reserva'),
    path('reserva/create/', EspacioCreateView.as_view(), name='reserva_create'),
    path('reserva/view/<int:pk>/', EspacioListView.as_view(), name='reserva_list'),
    path('reserva/edit/<int:pk>/', EspacioUpdateView.as_view(), name='reserva_edit'),
    path('reserva/delete/<int:pk>/', EspacioDeleteView.as_view(), name='reserva_delete'),
]
