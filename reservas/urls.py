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
    path('dashboard/<str:current_section>/', Crud.as_view(), name='crud'),
    path('dashboard/espacio/create/', EspacioCreateView.as_view(), name='espacio_create'),
    path('dashboard/espacio/list/', EspacioListView.as_view(), name='espacio_list'),
    path('dashboard/espacio/<int:pk>/view', EspacioListView.as_view(), name='espacio_list'),
    path('dashboard/espacio/<int:pk>/edit/', EspacioUpdateView.as_view(), name='espacio_edit'),
    path('dashboard/espacio/<int:pk>/delete/', EspacioDeleteView.as_view(), name='espacio_delete'),
]
